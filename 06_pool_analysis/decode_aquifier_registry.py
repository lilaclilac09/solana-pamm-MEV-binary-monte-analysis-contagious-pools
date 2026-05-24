"""Decode the Aquifier registry account layout.

Findings to date (from aquifier_analysis.json):
  - 8492-byte account CNC5TaeNQEoSPfQKZ7GgfM4R8WYAJRKRSHFCHkf2H7ko contains:
      SOL   @ offset 131
      PYUSD @ offset 527
      USDC  @ offset 1055
      USDT  @ offset 1121
  - 8552-byte account 5AVyF6qJBi8GxVjh6nh4Ew1DiJZugPxz9m58a8v2osk2 has no
    known base mints (likely config / oracle).

This script:
  1) Fetches both accounts' full raw bytes.
  2) Around each known mint, dumps the 64 bytes before and after to find
     entry boundaries (look for repeating delimiters, zero-padded blocks,
     name-shaped ASCII).
  3) Searches the 8552-byte account for ANY 32-byte chunk that decodes to a
     valid Solana mint (heuristic: appears in well-known mints, or has 3+
     pools owning it = SPL token account).
  4) Computes entry width hypotheses and persists to JSON.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time

import base58
import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
REGISTRY = "CNC5TaeNQEoSPfQKZ7GgfM4R8WYAJRKRSHFCHkf2H7ko"  # 8492 bytes
SECONDARY = "5AVyF6qJBi8GxVjh6nh4Ew1DiJZugPxz9m58a8v2osk2"  # 8552 bytes

KNOWN_MINT_OFFSETS = {
    "SOL":   131,
    "PYUSD": 527,
    "USDC":  1055,
    "USDT":  1121,
}
KNOWN_MINTS = {
    "SOL":   "So11111111111111111111111111111111111111112",
    "PYUSD": "2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",
    "USDC":  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT":  "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "JTO":   "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "JLP":   "27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4",
    "USD1":  "USD1ttGY1N7NvEzkZdxxKXNGJBV63MFK3tcQpzPxNGQ",
}


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


def fetch(pubkey: str) -> bytes:
    r = rpc("getAccountInfo", [pubkey, {"encoding": "base64"}])
    val = (r.get("result") or {}).get("value")
    return base64.b64decode(val["data"][0]) if val else b""


def hexdump(data: bytes, lo: int, hi: int, mark: int | None = None) -> str:
    lines = []
    for off in range(lo, hi, 16):
        chunk = data[off : off + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        marker = ""
        if mark is not None and off <= mark < off + 16:
            marker = f"  <-- mint here (col {mark - off})"
        lines.append(f"  {off:04x}  {hex_part:<47}  {ascii_part}{marker}")
    return "\n".join(lines)


def is_plausible_pubkey(b: bytes) -> bool:
    """Heuristic: not all zeros, not all ones, has reasonable byte entropy."""
    if len(b) != 32:
        return False
    if b == b"\x00" * 32 or b == b"\xff" * 32:
        return False
    # All-same-byte fillers are noise
    if len(set(b)) <= 2:
        return False
    return True


def find_all_plausible_pubkeys(data: bytes, stride: int = 1) -> list[int]:
    """Return offsets where bytes[off:off+32] looks like a real pubkey."""
    hits = []
    for off in range(0, len(data) - 32 + 1, stride):
        if is_plausible_pubkey(data[off : off + 32]):
            hits.append(off)
    return hits


def main():
    print(f"RPC: {RPC_URL}\n")
    reg = fetch(REGISTRY)
    sec = fetch(SECONDARY)
    print(f"Registry  {REGISTRY}  size={len(reg)}")
    print(f"Secondary {SECONDARY}  size={len(sec)}")

    out = {"registry_size": len(reg), "secondary_size": len(sec)}

    # ----- 1) Hexdump 64 bytes around each known mint in the registry -----
    print(f"\n=== Hex around known mints in registry ===")
    for name, off in KNOWN_MINT_OFFSETS.items():
        lo = max(0, off - 32)
        hi = min(len(reg), off + 32 + 32)  # 32 before, 32 of mint, 32 after
        print(f"\n--- {name} @ offset {off} ---")
        print(hexdump(reg, lo, hi, mark=off))

    # ----- 2) Entry width hypothesis -----
    print(f"\n=== Entry width hypotheses ===")
    ordered = sorted(KNOWN_MINT_OFFSETS.items(), key=lambda kv: kv[1])
    diffs = []
    for (n1, o1), (n2, o2) in zip(ordered, ordered[1:]):
        diff = o2 - o1
        print(f"  {n1} ({o1}) -> {n2} ({o2}): gap = {diff} bytes")
        diffs.append({"from": n1, "to": n2, "gap": diff})
    out["mint_gaps"] = diffs

    # Tiny entries are unlikely; gap of 66 (USDC->USDT) probably one entry
    # of (32 mint + ~34 metadata). Gaps of 396 / 528 suggest *strides* over
    # several entries — i.e., other mints we don't have in our known set live
    # between SOL@131 and PYUSD@527.
    print("\n  -> 66-byte USDC->USDT gap likely = 1 entry of ~66 bytes total")
    print("  -> 528-byte PYUSD->USDC and 396-byte SOL->PYUSD gaps = multi-entry jumps")
    print("     (other mints between them, not in our search list)")

    # ----- 3) Find ALL plausible pubkeys in registry (32-byte aligned) -----
    print(f"\n=== All plausible-pubkey offsets in registry (stride=66) ===")
    # If entry width is ~66 starting from SOL@131, all mints sit at
    # 131, 197, 263, ... — scan that lattice
    candidate_mints = []
    for off in range(131, len(reg) - 32, 66):
        b = reg[off : off + 32]
        if is_plausible_pubkey(b):
            mint = base58.b58encode(b).decode()
            candidate_mints.append({"offset": off, "mint": mint})
    print(f"  Found {len(candidate_mints)} candidate mints at offsets 131+66k")
    for c in candidate_mints[:30]:
        # Mark known
        label = next((n for n, m in KNOWN_MINTS.items() if m == c["mint"]), "")
        print(f"    @ {c['offset']:>5}  {c['mint']}  {label}")
    out["candidate_mints_stride_66"] = candidate_mints

    # ----- 4) Find ALL plausible pubkeys in secondary registry -----
    print(f"\n=== Plausible pubkeys in secondary registry (stride=8 scan) ===")
    sec_hits = find_all_plausible_pubkeys(sec, stride=8)
    print(f"  {len(sec_hits)} candidate pubkeys (stride=8)")
    # Sample a few
    sample = []
    for off in sec_hits[:20]:
        mint = base58.b58encode(sec[off : off + 32]).decode()
        label = next((n for n, m in KNOWN_MINTS.items() if m == mint), "")
        print(f"    @ {off:>5}  {mint}  {label}")
        sample.append({"offset": off, "candidate": mint, "label": label})
    out["secondary_candidates_sample"] = sample
    out["secondary_n_plausible_pubkeys"] = len(sec_hits)

    out_path = os.path.join(os.path.dirname(__file__), "aquifier_registry_decoded.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    sys.exit(main() or 0)
