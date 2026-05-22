"""Inspect HumidiFi pool raw bytes: dump hex, find pubkey-shaped 32-byte windows,
diff two pools to separate config (static) from state (changes), look for token
program / well-known program references that may hint at where mint refs live.
"""

from __future__ import annotations

import base64
import os

import base58
import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
HUMIDIFI_PROGRAM = "9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp"
SAMPLE_POOLS = [
    "8sKQHfjNhvmAw94PhfvfMcytmqW6jmxvwieYyzXCCPu",
    "AvGeFw71N5sNfV97mZ1uNrHg4yfufRicCJUrS9j2ehTX",
    "DB3sUCP2H4icbeKmK6yb6nUxU5ogbcRHtGuq7W2RoRwW",
    "3QYYvFWgSuGK8bbxMSAYkCqE8QfSuFtByagnZAuekia2",
]
# Programs/sysvars likely to be embedded as 32-byte references
KNOWN_REFS = {
    "TOKEN_PROGRAM":       "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "TOKEN_2022":          "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
    "ASSOCIATED_TOKEN":    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
    "SYSTEM_PROGRAM":      "11111111111111111111111111111111",
    "RENT_SYSVAR":         "SysvarRent111111111111111111111111111111111",
    "CLOCK_SYSVAR":        "SysvarC1ock11111111111111111111111111111111",
    "PROGRAM_ITSELF":      HUMIDIFI_PROGRAM,
}


def fetch(pubkey: str) -> bytes:
    r = requests.post(
        RPC_URL,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [pubkey, {"encoding": "base64"}],
        },
        timeout=20,
    ).json()
    return base64.b64decode(r["result"]["value"]["data"][0])


def find(data: bytes, needle: bytes) -> list[int]:
    out, start = [], 0
    while True:
        i = data.find(needle, start)
        if i == -1:
            return out
        out.append(i)
        start = i + 1


def hexdump(data: bytes, lo: int, hi: int) -> str:
    lines = []
    for off in range(lo, hi, 16):
        chunk = data[off : off + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"  {off:04x}  {hex_part:<47}  {ascii_part}")
    return "\n".join(lines)


def main() -> int:
    print(f"RPC: {RPC_URL}\n")
    accounts = {pk: fetch(pk) for pk in SAMPLE_POOLS}
    for pk, raw in accounts.items():
        print(f"{pk}  size={len(raw)}")
    print()

    # 1) Search for known program/sysvar refs in pool 0
    pk0 = SAMPLE_POOLS[0]
    raw0 = accounts[pk0]
    print(f"=== Known-ref scan on {pk0} ===")
    for name, addr in KNOWN_REFS.items():
        offs = find(raw0, base58.b58decode(addr))
        if offs:
            print(f"  {name:18s} @ {offs}")
        else:
            print(f"  {name:18s} -- not found")
    print()

    # 2) Header + tail hex dumps (likely contains discriminator + version)
    print(f"=== {pk0} header [0:64] ===")
    print(hexdump(raw0, 0, 64))
    print()
    print(f"=== {pk0} tail [{len(raw0)-64}:{len(raw0)}] ===")
    print(hexdump(raw0, len(raw0) - 64, len(raw0)))
    print()

    # 3) Diff pool0 vs pool1: stable bytes = config, varying = state
    pk1 = SAMPLE_POOLS[1]
    raw1 = accounts[pk1]
    same, diff = [], []
    n = min(len(raw0), len(raw1))
    for i in range(n):
        (same if raw0[i] == raw1[i] else diff).append(i)
    print(f"=== Byte diff: {pk0} vs {pk1} ===")
    print(f"  same: {len(same)} bytes  diff: {len(diff)} bytes")

    # Collapse runs of same/diff
    def runs(indices: list[int]) -> list[tuple[int, int]]:
        if not indices:
            return []
        out = [[indices[0], indices[0]]]
        for x in indices[1:]:
            if x == out[-1][1] + 1:
                out[-1][1] = x
            else:
                out.append([x, x])
        return [(a, b) for a, b in out]

    same_runs = runs(same)
    diff_runs = runs(diff)
    print(f"\n  Diff regions (likely state):")
    for a, b in diff_runs[:20]:
        print(f"    [{a:>5}, {b:>5}]  len={b - a + 1}")
    print(f"\n  Same regions >= 8 bytes (likely structural / shared config):")
    for a, b in same_runs:
        if b - a + 1 >= 8:
            print(f"    [{a:>5}, {b:>5}]  len={b - a + 1}")

    # 4) Header & tail of pool1 for comparison
    print(f"\n=== {pk1} header [0:64] ===")
    print(hexdump(raw1, 0, 64))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
