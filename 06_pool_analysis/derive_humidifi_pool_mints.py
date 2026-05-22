"""Derive (pool -> mint1, mint2) for HumidiFi via swap tx token-balance changes.

Pool accounts contain no mint refs (verified by inspect_humidifi_pool.py: ALL
89 accounts size=1728, [5:447] identical across pools, no SPL token program
references found). So we recover mints from the swap tx itself.

Method:
  1) Enumerate HumidiFi pools.
  2) For each pool, fetch a few recent signatures.
  3) Pull each tx with jsonParsed; collect the unique mints in
     postTokenBalances. The pool's mint pair is the set of mints that
     consistently appear across the pool's recent swaps.
"""

from __future__ import annotations

import json
import os
import time
from collections import Counter

import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
HUMIDIFI_PROGRAM = "9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp"
ACCOUNT_SIZE = 1728
SIGS_PER_POOL = 5  # sample size — mint pair must be stable across this many txs


def rpc(method: str, params: list, retries: int = 5) -> dict:
    backoff = 1.0
    for _ in range(retries):
        r = requests.post(
            RPC_URL,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            timeout=30,
        )
        if r.status_code == 429:
            time.sleep(backoff)
            backoff *= 2
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("rate limited after retries")


def list_pools() -> list[str]:
    res = rpc(
        "getProgramAccounts",
        [
            HUMIDIFI_PROGRAM,
            {
                "encoding": "base64",
                "dataSlice": {"offset": 0, "length": 0},
                "filters": [{"dataSize": ACCOUNT_SIZE}],
            },
        ],
    )
    accts = res["result"]
    accts.sort(key=lambda a: -a["account"]["lamports"])
    return [a["pubkey"] for a in accts]


def recent_sigs(pool: str, limit: int) -> list[str]:
    res = rpc("getSignaturesForAddress", [pool, {"limit": limit}])
    return [item["signature"] for item in res.get("result", [])]


def tx_mints(sig: str) -> set[str]:
    res = rpc(
        "getTransaction",
        [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
    )
    tx = res.get("result")
    if not tx or not tx.get("meta"):
        return set()
    mints: set[str] = set()
    for bal in tx["meta"].get("postTokenBalances") or []:
        m = bal.get("mint")
        if m:
            mints.add(m)
    for bal in tx["meta"].get("preTokenBalances") or []:
        m = bal.get("mint")
        if m:
            mints.add(m)
    return mints


def stable_pair(sig_mints: list[set[str]]) -> list[str]:
    """A pool's mint pair is the mints that appear in MOST txs (>= half)."""
    counter: Counter[str] = Counter()
    for s in sig_mints:
        for m in s:
            counter[m] += 1
    threshold = max(1, len(sig_mints) // 2)
    stable = [m for m, c in counter.most_common() if c >= threshold]
    return stable[:2]  # top-2 most-stable mints = the pool's pair


def derive(pool_limit: int) -> list[dict]:
    pools = list_pools()[:pool_limit]
    out: list[dict] = []
    for i, pool in enumerate(pools):
        try:
            sigs = recent_sigs(pool, SIGS_PER_POOL)
        except Exception as e:
            print(f"  [{i+1}/{len(pools)}] {pool}: sigs error {e}")
            continue
        sig_mints: list[set[str]] = []
        for s in sigs:
            try:
                sig_mints.append(tx_mints(s))
            except Exception as e:
                print(f"    tx {s[:16]}... error: {e}")
            time.sleep(0.25)
        pair = stable_pair(sig_mints)
        out.append({"pool": pool, "n_txs_sampled": len(sig_mints), "mints": pair})
        print(f"  [{i+1}/{len(pools)}] {pool}: {pair}")
        time.sleep(0.25)
    return out


def main() -> int:
    print(f"RPC: {RPC_URL}")
    print(f"HumidiFi program: {HUMIDIFI_PROGRAM}\n")
    results = derive(pool_limit=15)
    out_path = os.path.join(os.path.dirname(__file__), "humidifi_pool_mints.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    n = sum(1 for r in results if len(r["mints"]) >= 2)
    print(f"\n{n}/{len(results)} pools resolved (>=2 stable mints)")
    print(f"Saved to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
