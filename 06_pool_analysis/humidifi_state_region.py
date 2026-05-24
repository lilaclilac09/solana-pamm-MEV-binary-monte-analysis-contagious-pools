"""Inspect HumidiFi pool state region [448:543] across multiple pools.

From HUMIDIFI_REVERSE_ENGINEERING.md: the 96-byte window [448:543] is one of
the two regions that *changes* between pool snapshots (the other being a
5-byte header). The static [5:447] block is shared config across pools.

Hypothesis: [448:543] encodes reserves + oracle price + last update slot.

This script:
  1) Snapshots the top-lamports pools twice (5 min apart) so we can see what
     bytes change WITHIN a pool over time (= state ticks).
  2) For each pool, parses [448:543] under several layout hypotheses:
       H1: 12 x u64  (96 / 8)
       H2: 6 x u128  (96 / 16)
       H3: 2 x (u64 reserve_base, u64 reserve_quote, u64 oracle_price,
                u64 last_slot, u64 fee_acc, u64 reserved)  -- 48 bytes per side
  3) Cross-references each parsed u64 with current slot number (~330M)
     to find slot-like fields, and computes plausible price ratios to find
     oracle/reserve fields.
  4) Dumps hex of [448:543] alongside parsed values for human inspection.
"""

from __future__ import annotations

import base64
import json
import os
import struct
import time

import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
STATE_LO, STATE_HI = 448, 544  # 96 bytes
POOLS = [  # top-lamports HumidiFi pools (from earlier scans)
    "8sKQHfjNhvmAw94PhfvfMcytmqW6jmxvwieYyzXCCPu",
    "AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX",
    "DB3sUCP2H4icbeKmK6yb6nUxU5ogbcRHtGuq7W2RoRwW",
    "3QYYvFWgSuGK8bbxMSAYkCqE8QfSuFtByagnZAuekia2",
    "5dhYayH9qvzNyCPoh2hKN8TJqumoGsWdyZ9UfPLXBfD9",
    "6n9VhCwQ7EwK6NqFDjnHPzEk6wZdRBTfh43RFgHQWHuQ",
]
SNAPSHOT_GAP_SEC = 90  # short enough to keep total runtime reasonable


def rpc(method, params):
    backoff = 2.0
    for _ in range(6):
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
        except (requests.exceptions.RequestException, OSError):
            time.sleep(backoff); backoff = min(backoff * 1.7, 30)
    return {"error": "exhausted"}


def get_slot() -> int:
    return rpc("getSlot", []).get("result", 0)


def fetch_state(pool: str) -> bytes:
    r = rpc("getAccountInfo", [pool, {"encoding": "base64"}])
    val = (r.get("result") or {}).get("value")
    if not val:
        return b""
    raw = base64.b64decode(val["data"][0])
    return raw[STATE_LO:STATE_HI]


def snapshot_all() -> dict[str, bytes]:
    out = {}
    for pk in POOLS:
        out[pk] = fetch_state(pk)
        time.sleep(0.4)
    return out


def parse_u64s(b: bytes) -> list[int]:
    return list(struct.unpack(f"<{len(b)//8}Q", b[: (len(b) // 8) * 8]))


def parse_u128s(b: bytes) -> list[int]:
    n = len(b) // 16
    out = []
    for i in range(n):
        lo, hi = struct.unpack("<QQ", b[i * 16 : (i + 1) * 16])
        out.append(lo | (hi << 64))
    return out


def hexline(b: bytes) -> str:
    return " ".join(f"{x:02x}" for x in b)


def classify_u64(value: int, current_slot: int) -> list[str]:
    tags = []
    if value == 0:
        tags.append("zero")
        return tags
    if abs(value - current_slot) < 1_000_000:
        tags.append("≈ current_slot")
    elif current_slot * 0.5 < value < current_slot * 1.5:
        tags.append("slot-range")
    if 10**6 < value < 10**12:
        tags.append("reserve-scale (1e6-1e12)")
    if 10**12 < value < 10**16:
        tags.append("price-scale (1e12-1e16)")
    if 10**18 < value < 10**21:
        tags.append("u128-low-half or huge supply")
    if value > 10**18:
        tags.append("very large")
    return tags


def main():
    print(f"RPC: {RPC_URL}")
    slot0 = get_slot()
    print(f"slot at start: {slot0}\n")

    print(f"Snapshot 1...")
    snap1 = snapshot_all()

    print(f"Sleeping {SNAPSHOT_GAP_SEC}s for state to tick...")
    time.sleep(SNAPSHOT_GAP_SEC)

    print(f"Snapshot 2...")
    snap2 = snapshot_all()
    slot1 = get_slot()
    print(f"slot at end:   {slot1}  (Δ {slot1 - slot0} slots)\n")

    findings = {"slot_start": slot0, "slot_end": slot1, "pools": {}}

    for pk in POOLS:
        s1 = snap1.get(pk, b"")
        s2 = snap2.get(pk, b"")
        if not s1 or not s2:
            print(f"--- {pk}: empty fetch, skipped ---")
            continue
        u1 = parse_u64s(s1)
        u2 = parse_u64s(s2)
        deltas = [b - a for a, b in zip(u1, u2)]
        same = sum(1 for d in deltas if d == 0)
        print(f"\n=== {pk} ===")
        print(f"  s1 hex: {hexline(s1[:48])}")
        print(f"          {hexline(s1[48:96])}")
        print(f"  s2 hex: {hexline(s2[:48])}")
        print(f"          {hexline(s2[48:96])}")
        print(f"  u64 lane | snap1 | snap2 | delta | tags(snap2 vs slot)")
        rows = []
        for i, (a, b, d) in enumerate(zip(u1, u2, deltas)):
            tags = classify_u64(b, slot1)
            print(f"    [{i:>2}] {a:>20}  {b:>20}  {d:>+12}  {tags}")
            rows.append({"lane": i, "snap1": a, "snap2": b, "delta": d, "tags": tags})
        # Also dump 6 x u128 view
        u128_1 = parse_u128s(s1)
        u128_2 = parse_u128s(s2)
        u128_view = []
        print(f"  u128 lanes (snap1 / snap2):")
        for i, (a, b) in enumerate(zip(u128_1, u128_2)):
            tag = "ratio-shape" if (a and b and 0.5 < a / b < 2 and a != b) else ""
            print(f"    [{i:>2}] {a}  /  {b}  {tag}")
            u128_view.append({"lane": i, "snap1": str(a), "snap2": str(b), "tag": tag})

        findings["pools"][pk] = {
            "n_lanes_unchanged_u64": same,
            "u64_lanes": rows,
            "u128_lanes": u128_view,
        }

    out_path = os.path.join(os.path.dirname(__file__), "humidifi_state_region_decoded.json")
    with open(out_path, "w") as f:
        json.dump(findings, f, indent=2)
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
