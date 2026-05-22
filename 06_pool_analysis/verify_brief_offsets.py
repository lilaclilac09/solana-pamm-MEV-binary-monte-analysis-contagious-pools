"""Validate the brief's mint-offset table against live on-chain data.

For each PAMM with a published (mint1_offset, mint2_offset) in
PAMM_RESEARCH_BRIEF.md, pull 5 pool accounts, decode the bytes at the claimed
offsets, and check that they parse as plausible SPL mints (32 bytes, base58
encodable, ideally appearing in many pools = shared base mint like SOL/USDC).
"""

from __future__ import annotations

import base64
import json
import os
import time
from collections import Counter

import base58
import requests

RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

PAMMS = {
    "bisonfi":  {"program": "BiSoNHVpsVZW2F7rx2eQ59yQwKxzU5NvBcmKshCSUypi", "size": 2048, "m1": 184, "m2": 216},
    "tessera":  {"program": "TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH",  "size": 1264, "m1": 56,  "m2": 24},
    "alphaQ":   {"program": "ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA", "size": 672,  "m1": 272, "m2": 240},
    "solfi":    {"program": "SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe",  "size": 2800, "m1": 2696,"m2": 2664},
    "solfiv2":  {"program": "SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF",  "size": 1728, "m1": 88,  "m2": 56},
    "goonfiv2": {"program": "goonuddtQRrWqqn5nFyczVKaie28f3kDkHWkHtURSLE",  "size": 2048, "m1": 112, "m2": 80},
    "zerofi":   {"program": "ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY",  "size": 7456, "m1": 104, "m2": 72},
    "obricv2":  {"program": "obriQD1zbpyLz95G5n7nJe6a4DPjpFwa5XYPoNm113y",  "size": 666,  "m1": 202, "m2": 234},
}

KNOWN_BASE_MINTS = {
    "So11111111111111111111111111111111111111112": "SOL",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
}


def rpc(method, params, retries=5):
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
    raise RuntimeError("rate limited")


def sample_pools(program, size, n=5):
    res = rpc(
        "getProgramAccounts",
        [
            program,
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
    return [a["pubkey"] for a in accts[:n]]


def fetch_data(pubkeys):
    out = {}
    res = rpc("getMultipleAccounts", [pubkeys, {"encoding": "base64"}])
    for pk, acc in zip(pubkeys, res["result"]["value"]):
        if acc is not None:
            out[pk] = base64.b64decode(acc["data"][0])
    return out


def is_valid_mint_bytes(b: bytes) -> bool:
    """Heuristic: a real mint pubkey is rarely all zeros and rarely all 0xff."""
    if len(b) != 32:
        return False
    if b == b"\x00" * 32 or b == b"\xff" * 32:
        return False
    return True


def main():
    print(f"RPC: {RPC_URL}\n")
    out = []
    for name, cfg in PAMMS.items():
        print(f"=== {name} (size={cfg['size']}, m1={cfg['m1']}, m2={cfg['m2']}) ===")
        pools = sample_pools(cfg["program"], cfg["size"], n=5)
        if not pools:
            print(f"  no pools found (size filter may be wrong)\n")
            out.append({"pamm": name, "status": "no_pools"})
            continue
        data = fetch_data(pools)
        m1_seen, m2_seen = Counter(), Counter()
        m1_labels, m2_labels = [], []
        for pk, raw in data.items():
            if len(raw) < max(cfg["m1"], cfg["m2"]) + 32:
                print(f"  {pk}: data too short ({len(raw)})")
                continue
            m1 = raw[cfg["m1"] : cfg["m1"] + 32]
            m2 = raw[cfg["m2"] : cfg["m2"] + 32]
            m1_b58 = base58.b58encode(m1).decode() if is_valid_mint_bytes(m1) else "<invalid>"
            m2_b58 = base58.b58encode(m2).decode() if is_valid_mint_bytes(m2) else "<invalid>"
            m1_seen[m1_b58] += 1
            m2_seen[m2_b58] += 1
            print(f"  {pk}")
            print(f"    m1@{cfg['m1']:>5}: {m1_b58}  ({KNOWN_BASE_MINTS.get(m1_b58, '?')})")
            print(f"    m2@{cfg['m2']:>5}: {m2_b58}  ({KNOWN_BASE_MINTS.get(m2_b58, '?')})")
            m1_labels.append(m1_b58)
            m2_labels.append(m2_b58)
        # Verdict: are most pools yielding distinct, valid-looking mints?
        n = len(data)
        m1_valid = sum(1 for x in m1_labels if x != "<invalid>")
        m2_valid = sum(1 for x in m2_labels if x != "<invalid>")
        # how many m1 values are well-known base mints (sanity check)
        m1_known = sum(1 for x in m1_labels if x in KNOWN_BASE_MINTS)
        m2_known = sum(1 for x in m2_labels if x in KNOWN_BASE_MINTS)
        verdict = (
            "GOOD" if m1_valid == n and m2_valid == n and (m1_known + m2_known) >= 1
            else "DUBIOUS"
        )
        print(f"  verdict: {verdict}  (m1_valid={m1_valid}/{n}, m2_valid={m2_valid}/{n}, known_quote_hits={m1_known + m2_known})\n")
        out.append({
            "pamm": name,
            "size": cfg["size"],
            "verdict": verdict,
            "n_pools_checked": n,
            "m1_valid": m1_valid,
            "m2_valid": m2_valid,
            "m1_known_base_mint_hits": m1_known,
            "m2_known_base_mint_hits": m2_known,
            "m1_samples": dict(m1_seen),
            "m2_samples": dict(m2_seen),
        })
        time.sleep(0.4)

    out_path = os.path.join(os.path.dirname(__file__), "brief_offsets_verification.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSummary written to {out_path}")
    print(f"\n=== Verdicts ===")
    for r in out:
        print(f"  {r['pamm']:10s}: {r.get('verdict', r.get('status'))}")


if __name__ == "__main__":
    main()
