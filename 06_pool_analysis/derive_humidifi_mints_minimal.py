"""Minimal HumidiFi pool -> mints resolver. Single tx per pool, hardcoded pool
list (from inspect_humidifi_pool.py), aggressive backoff for public RPC.

Goal: produce a working (pool, mint1, mint2) row for at least a few HumidiFi
pools to prove the methodology, then scale up with a paid RPC.
"""

from __future__ import annotations

import json
import os
import sys
import time

import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# Top-lamports pools from earlier getProgramAccounts run
POOLS = [
    "8sKQHfjNhvmAw94PhfvfMcytmqW6jmxvwieYyzXCCPu",
    "AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX",
    "DB3sUCP2H4icbeKmK6yb6nUxU5ogbcRHtGuq7W2RoRwW",
    "3QYYvFWgSuGK8bbxMSAYkCqE8QfSuFtByagnZAuekia2",
    "5dhYayH9qvzNyCPoh2hKN8TJqumoGsWdyZ9UfPLXBfD9",
    "FksffEqnBRixYGR791Qw2MgdU7zNCpHVFYBL4Fa4qVuH",
    "6n9VhCwQ7EwK6NqFDjnHPzEk6wZdRBTfh43RFgHQWHuQ",
    "iAMtZieUtpLwB3dzWw8Fo3H3FPkMFy3ej52URusseR1",
    "AYZ1amnDbDzsDVmnsFjsMDVJsJXaEEDHJsbCDnkTcdUM",
    "GD5eJhDmVcosRoU2H27LoFCuYERMTe4Mf1ooban6ba9T",
    "9c5xYTnURgpQLDk4XqkJdaUab6p8EMBgE5n7n29pQzCy",
    "H3TyE2Q3rDrvRXD8PzHYE7BS2hafGuybje4qXCtyWqMH",
]

# Tokens almost always present as side-effect fees / wraps; ignore them when
# narrowing to the actual pool pair
NOISE_MINTS: set[str] = set()


def rpc(method, params):
    backoff = 2.0
    for attempt in range(6):
        try:
            r = requests.post(
                RPC_URL,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                timeout=30,
            )
            if r.status_code == 429:
                print(f"    [429] sleeping {backoff:.1f}s", flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 1.7, 30)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"    [err {attempt}] {e}; sleep {backoff:.1f}s", flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 1.7, 30)
    return {"error": "exhausted retries"}


def tx_mints(sig: str) -> set[str]:
    r = rpc(
        "getTransaction",
        [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}],
    )
    tx = r.get("result")
    if not tx or not tx.get("meta"):
        return set()
    mints: set[str] = set()
    for bal in (tx["meta"].get("postTokenBalances") or []):
        if (m := bal.get("mint")):
            mints.add(m)
    for bal in (tx["meta"].get("preTokenBalances") or []):
        if (m := bal.get("mint")):
            mints.add(m)
    return mints - NOISE_MINTS


def main():
    print(f"RPC: {RPC_URL}", flush=True)
    results = []
    for i, pool in enumerate(POOLS):
        print(f"[{i+1}/{len(POOLS)}] {pool}", flush=True)
        r = rpc("getSignaturesForAddress", [pool, {"limit": 8}])
        sigs = [s["signature"] for s in (r.get("result") or [])]
        if not sigs:
            print(f"   no sigs", flush=True)
            continue
        # Walk back through sigs until we find one with token balances (a swap)
        found: set[str] = set()
        used_sig = None
        for s in sigs:
            ms = tx_mints(s)
            if ms:
                found = ms
                used_sig = s
                break
            time.sleep(0.4)
        print(f"   sig={(used_sig or '?')[:24]}... mints={sorted(found)}", flush=True)
        results.append({"pool": pool, "sig": used_sig, "mints": sorted(found)})
        time.sleep(0.8)

    out = os.path.join(os.path.dirname(__file__), "humidifi_pool_mints.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} rows -> {out}", flush=True)
    print(f"\n=== Summary ===")
    for r in results:
        print(f"  {r['pool']}: {r['mints']}")


if __name__ == "__main__":
    sys.exit(main() or 0)
