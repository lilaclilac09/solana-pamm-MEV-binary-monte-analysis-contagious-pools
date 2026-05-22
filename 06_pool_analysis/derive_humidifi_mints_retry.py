"""Retry the still-empty HumidiFi pools with a deeper signature lookback (20)."""

from __future__ import annotations

import json
import os
import sys
import time

import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
IN_PATH = os.path.join(os.path.dirname(__file__), "humidifi_pool_mints.json")


def rpc(method, params):
    backoff = 2.0
    for _ in range(8):
        try:
            r = requests.post(
                RPC_URL,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                timeout=30,
            )
            if r.status_code == 429:
                time.sleep(backoff); backoff = min(backoff * 1.7, 30); continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException:
            time.sleep(backoff); backoff = min(backoff * 1.7, 30)
    return {"error": "exhausted"}


def tx_mints(sig):
    r = rpc("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
    tx = r.get("result")
    if not tx or not tx.get("meta"):
        return set()
    mints = set()
    for k in ("postTokenBalances", "preTokenBalances"):
        for bal in (tx["meta"].get(k) or []):
            if (m := bal.get("mint")):
                mints.add(m)
    return mints


def main():
    with open(IN_PATH) as f:
        rows = json.load(f)
    empty = [r for r in rows if not r["mints"]]
    print(f"Retrying {len(empty)} empty pools with deeper sig lookback", flush=True)
    for i, row in enumerate(empty):
        pool = row["pool"]
        print(f"[{i+1}/{len(empty)}] {pool}", flush=True)
        r = rpc("getSignaturesForAddress", [pool, {"limit": 25}])
        sigs = [s["signature"] for s in (r.get("result") or [])]
        found = set(); used = None
        for s in sigs:
            ms = tx_mints(s)
            if ms:
                found, used = ms, s
                break
            time.sleep(0.4)
        row["mints"] = sorted(found)
        row["sig"] = used
        print(f"   -> mints={sorted(found)}", flush=True)
        time.sleep(0.8)
    with open(IN_PATH, "w") as f:
        json.dump(rows, f, indent=2)
    n = sum(1 for r in rows if len(r["mints"]) >= 2)
    print(f"\n{n}/{len(rows)} pools fully resolved")
    for r in rows:
        print(f"  {r['pool']}: {r['mints']}")


if __name__ == "__main__":
    sys.exit(main() or 0)
