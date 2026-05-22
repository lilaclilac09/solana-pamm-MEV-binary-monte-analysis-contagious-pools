"""Aquifier reverse engineering: find mint offsets (if any), and resolve
(pool -> mint1, mint2) via tx fallback.

Same playbook as HumidiFi, parameterized for Aquifier.

Aquifier program: AQU1FRd7papthgdrwPTTq5JacJh8YtwEXaBfKU3bTz45
Account sizes observed:
  - 1056 x 35 (pool accounts)
  -  8492 x 1 (possible registry)
  -  8552 x 1 (possible registry v2)

Steps:
  1) Sample several 1056-byte pools; search for known SPL mints (SOL, USDC,
     USDT) at every offset. If found at consistent offsets across pools, that
     IS the answer — publish offsets.
  2) If pools have no mints, inspect the 8492/8552 registry accounts the same
     way; mints may live there.
  3) Independently, derive (pool, mints) via tx postTokenBalances (the
     HumidiFi-proven fallback). Persists humidifi-style JSON.
"""

from __future__ import annotations

import base64
import json
import os
import time
from collections import Counter, defaultdict

import base58
import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
AQUIFIER_PROGRAM = "AQU1FRd7papthgdrwPTTq5JacJh8YtwEXaBfKU3bTz45"
POOL_SIZE = 1056
REGISTRY_SIZES = [8492, 8552]
SAMPLE_POOLS = 8
TX_LOOKBACK = 8

KNOWN_MINTS = {
    "SOL":   "So11111111111111111111111111111111111111112",
    "USDC":  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT":  "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "JTO":   "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "JLP":   "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",
    "PYUSD": "2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",
    "USD1":  "USD1ttGY1N7NvEzkZdxxKXNGJBV63MFK3tcQpzPxNGQ",
}


def rpc(method, params):
    backoff = 2.0
    for attempt in range(8):
        try:
            r = requests.post(
                RPC_URL,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                timeout=30,
            )
            if r.status_code == 429:
                print(f"    [429 attempt {attempt}] sleep {backoff:.1f}s", flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 1.7, 30)
                continue
            r.raise_for_status()
            return r.json()
        except (requests.exceptions.RequestException, OSError) as e:
            print(f"    [net err attempt {attempt}] {type(e).__name__}; sleep {backoff:.1f}s", flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 1.7, 30)
    return {"error": "exhausted retries"}


def list_pools_by_size(size):
    res = rpc(
        "getProgramAccounts",
        [
            AQUIFIER_PROGRAM,
            {
                "encoding": "base64",
                "dataSlice": {"offset": 0, "length": 0},
                "filters": [{"dataSize": size}],
            },
        ],
    )
    if "error" in res:
        return []
    accts = res["result"]
    accts.sort(key=lambda a: -a["account"]["lamports"])
    return [a["pubkey"] for a in accts]


def fetch_data(pubkey):
    r = rpc("getAccountInfo", [pubkey, {"encoding": "base64"}])
    val = (r.get("result") or {}).get("value")
    if not val:
        return None
    return base64.b64decode(val["data"][0])


def search_mints(data, label):
    print(f"\n=== Mint search in {label} (size {len(data)}) ===")
    any_hit = False
    for name, addr in KNOWN_MINTS.items():
        b = base58.b58decode(addr)
        idx = data.find(b)
        if idx != -1:
            print(f"  {name:6s} found at offset {idx}")
            any_hit = True
    if not any_hit:
        print("  (no known mints found)")
    return any_hit


def find_offset_pattern_across_pools(pools_data):
    """For each known mint, record offsets where it appears, per pool.
    Returns offsets that recur across pools (= structural mint slots)."""
    offset_counter: Counter[int] = Counter()
    offset_to_mints: dict[int, set[str]] = defaultdict(set)
    pool_finds: list[dict] = []
    for pk, raw in pools_data.items():
        row = {"pool": pk, "hits": {}}
        for name, addr in KNOWN_MINTS.items():
            b = base58.b58decode(addr)
            start = 0
            while True:
                idx = raw.find(b, start)
                if idx == -1:
                    break
                row["hits"].setdefault(name, []).append(idx)
                offset_counter[idx] += 1
                offset_to_mints[idx].add(name)
                start = idx + 1
        pool_finds.append(row)
    top = offset_counter.most_common(10)
    return pool_finds, top, {o: sorted(s) for o, s in offset_to_mints.items()}


def tx_mints_for_pool(pool):
    r = rpc("getSignaturesForAddress", [pool, {"limit": TX_LOOKBACK}])
    sigs = [s["signature"] for s in (r.get("result") or [])]
    for s in sigs:
        r = rpc(
            "getTransaction",
            [s, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
        )
        tx = r.get("result")
        if not tx or not tx.get("meta"):
            continue
        mints: set[str] = set()
        for bal in (tx["meta"].get("postTokenBalances") or []):
            if (m := bal.get("mint")):
                mints.add(m)
        for bal in (tx["meta"].get("preTokenBalances") or []):
            if (m := bal.get("mint")):
                mints.add(m)
        if mints:
            return s, sorted(mints)
        time.sleep(0.4)
    return None, []


def main():
    out = {"rpc": RPC_URL, "program": AQUIFIER_PROGRAM}
    print(f"RPC: {RPC_URL}")
    print(f"Aquifier program: {AQUIFIER_PROGRAM}\n")

    # ----------- 1) Inspect pool accounts (size 1056) -----------
    pool_pubkeys = list_pools_by_size(POOL_SIZE)
    print(f"Found {len(pool_pubkeys)} pools at size {POOL_SIZE}")
    sample = pool_pubkeys[:SAMPLE_POOLS]
    pools_data = {}
    for pk in sample:
        d = fetch_data(pk)
        if d is not None:
            pools_data[pk] = d
        time.sleep(0.4)
    print(f"Fetched {len(pools_data)} pool accounts\n")

    # Quick per-pool single-pass scan
    for pk, raw in pools_data.items():
        search_mints(raw, pk[:16] + "...")

    # Cross-pool offset aggregation
    pool_finds, top_offsets, offset_mints = find_offset_pattern_across_pools(pools_data)
    print(f"\n=== Top offsets across {len(pools_data)} pools ===")
    if not top_offsets:
        print("  (none found — pools have no plaintext mint bytes)")
    for off, cnt in top_offsets:
        print(f"  offset {off:>5}  count {cnt:>3}  mints {offset_mints[off]}")
    out["pool_scan"] = {
        "n_pools": len(pools_data),
        "pool_finds": pool_finds,
        "top_offsets": top_offsets,
    }

    # ----------- 2) Inspect registry accounts -----------
    out["registry_scan"] = []
    for size in REGISTRY_SIZES:
        regs = list_pools_by_size(size)
        for pk in regs:
            print(f"\n--- Registry candidate {pk} size={size} ---")
            d = fetch_data(pk)
            if d is None:
                continue
            # Count occurrences of each known mint
            hits = {}
            for name, addr in KNOWN_MINTS.items():
                b = base58.b58decode(addr)
                offs = []
                start = 0
                while (i := d.find(b, start)) != -1:
                    offs.append(i)
                    start = i + 1
                if offs:
                    hits[name] = offs
            print(f"  mint hits: {hits}")
            out["registry_scan"].append({"pubkey": pk, "size": size, "mint_hits": hits})
            time.sleep(0.3)

    # Write partial result NOW so a late crash doesn't lose scan/registry data
    out_path = os.path.join(os.path.dirname(__file__), "aquifier_analysis.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n(partial result saved -> {out_path})")

    # ----------- 3) tx-based mint derivation for ALL pools -----------
    print(f"\n=== Resolving (pool -> mints) via tx for all {len(pool_pubkeys)} pools ===")
    pool_mints = []
    for i, pk in enumerate(pool_pubkeys):
        try:
            sig, ms = tx_mints_for_pool(pk)
        except Exception as e:
            print(f"  [{i+1}/{len(pool_pubkeys)}] {pk}: ERROR {type(e).__name__}", flush=True)
            sig, ms = None, []
        print(f"  [{i+1}/{len(pool_pubkeys)}] {pk}: {ms}", flush=True)
        pool_mints.append({"pool": pk, "sig": sig, "mints": ms})
        # Persist every 5 pools so we never lose progress
        if (i + 1) % 5 == 0 or i == len(pool_pubkeys) - 1:
            out["pool_mints"] = pool_mints
            with open(out_path, "w") as f:
                json.dump(out, f, indent=2)
        time.sleep(0.6)
    out["pool_mints"] = pool_mints
    n_resolved = sum(1 for r in pool_mints if len(r["mints"]) >= 2)
    print(f"\nResolved {n_resolved}/{len(pool_mints)} pools")

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFinal saved -> {out_path}")


if __name__ == "__main__":
    main()
