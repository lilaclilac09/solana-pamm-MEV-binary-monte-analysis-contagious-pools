"""Reverse-engineer HumidiFi pool account layout: find mint1/mint2 byte offsets.

Method: fetch raw bytes for N HumidiFi pools, then for each well-known SPL mint
(SOL, USDC, USDT) search for its 32-byte pubkey inside the account data. The
offset that consistently appears across pools is a mint slot.
"""

from __future__ import annotations

import base64
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Iterable

import base58
import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
HUMIDIFI_PROGRAM = "9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp"
ACCOUNT_SIZE = 1728
SAMPLE_POOLS = 12

KNOWN_MINTS = {
    "SOL":  "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "JTO":  "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "JLP":  "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",
    "PYUSD":"2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",
    "USD1": "USD1ttGY1N7NvEzkZdxxKXNGJBV63MFK3tcQpzPxNGQ",
}


def rpc(method: str, params: list) -> dict:
    r = requests.post(
        RPC_URL,
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def list_pool_pubkeys(limit: int) -> list[str]:
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
    if "error" in res:
        raise RuntimeError(f"getProgramAccounts failed: {res['error']}")
    accounts = res["result"]
    accounts.sort(key=lambda a: -a["account"]["lamports"])  # heuristic: bigger pools first
    return [a["pubkey"] for a in accounts[:limit]]


def fetch_account_data(pubkeys: list[str]) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for i in range(0, len(pubkeys), 100):
        chunk = pubkeys[i : i + 100]
        res = rpc("getMultipleAccounts", [chunk, {"encoding": "base64"}])
        for pk, acc in zip(chunk, res["result"]["value"]):
            if acc is None:
                continue
            out[pk] = base64.b64decode(acc["data"][0])
    return out


def find_offsets(data: bytes, needle: bytes) -> list[int]:
    hits, start = [], 0
    while True:
        idx = data.find(needle, start)
        if idx == -1:
            return hits
        hits.append(idx)
        start = idx + 1


def reverse_mint_offsets(account_data: dict[str, bytes]) -> dict:
    mint_bytes = {name: base58.b58decode(addr) for name, addr in KNOWN_MINTS.items()}
    # symbol -> list of offsets observed per pool (one row per pool)
    per_pool: list[dict] = []
    offset_counter: Counter[int] = Counter()
    offset_to_mints: dict[int, set[str]] = defaultdict(set)

    for pubkey, raw in account_data.items():
        row = {"pool": pubkey, "hits": {}}
        for sym, b in mint_bytes.items():
            offsets = find_offsets(raw, b)
            if offsets:
                row["hits"][sym] = offsets
                for o in offsets:
                    offset_counter[o] += 1
                    offset_to_mints[o].add(sym)
        per_pool.append(row)

    # Offsets that appear in many pools are structural slots; cherry-pick top 2.
    top = offset_counter.most_common(10)
    return {
        "pools": per_pool,
        "top_offsets": top,
        "offset_mints": {o: sorted(s) for o, s in offset_to_mints.items()},
    }


def main() -> int:
    print(f"RPC: {RPC_URL}")
    print(f"HumidiFi program: {HUMIDIFI_PROGRAM}  size={ACCOUNT_SIZE}")
    print(f"Listing top {SAMPLE_POOLS} pools by lamports...")
    pubkeys = list_pool_pubkeys(SAMPLE_POOLS)
    print(f"  -> {len(pubkeys)} pools")
    for pk in pubkeys:
        print(f"     {pk}")

    print("Fetching raw account data...")
    data = fetch_account_data(pubkeys)
    print(f"  -> {len(data)} accounts decoded")

    print("Searching for known mint bytes inside each pool...")
    result = reverse_mint_offsets(data)

    print("\n=== Per-pool hits ===")
    for row in result["pools"]:
        print(f"{row['pool']}")
        for sym, offs in row["hits"].items():
            print(f"  {sym:6s} @ {offs}")

    print("\n=== Top offsets across pools (offset -> hit-count, mints) ===")
    for off, cnt in result["top_offsets"]:
        mints = result["offset_mints"][off]
        print(f"  offset {off:>5}  count {cnt:>3}  mints {mints}")

    out_path = os.path.join(os.path.dirname(__file__), "humidifi_offset_evidence.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nEvidence written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
