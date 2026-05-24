"""Pull Jupiter's program-id-to-label table and surface PAMMs not yet covered
in this project.

Jupiter integrates virtually every Solana AMM/DEX that meaningfully trades.
Diffing the full list against the 10 known prop AMMs from PAMM_RESEARCH_BRIEF.md
reveals candidate new prop AMMs to study (closed-source / unknown / non-classic).

Output: discovered_pamms.json with:
  - all_jupiter_programs: full label table
  - known_pamms: the 10 we already cover
  - candidate_new_pamms: heuristic-flagged programs worth investigating
  - classic_amms: well-known open AMMs we skip (Raydium/Orca/Meteora/etc.)
"""

from __future__ import annotations

import base64
import json
import os
import re
import time

import requests

JUP_URL = "https://lite-api.jup.ag/swap/v1/program-id-to-label"
RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# 10 PAMMs from PAMM_RESEARCH_BRIEF.md — already covered in this repo
KNOWN_PAMMS = {
    "BiSoNHVpsVZW2F7rx2eQ59yQwKxzU5NvBcmKshCSUypi": "bisonfi",
    "TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH":  "tessera",
    "ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA": "alphaQ",
    "SoLFiHG9TfgtdUXUjWAxi3LtvYuFyDLVhBWxdMZxyCe":  "solfi",
    "SV2EYYJyRz2YhfXwXnhNAevDEui5Q6yrfyo13WtupPF":  "solfiv2",
    "goonuddtQRrWqqn5nFyczVKaie28f3kDkHWkHtURSLE":  "goonfiv2",
    "ZERor4xhbUycZ6gb9ntrhqscUcZmAbQDjEAtCf4hbZY":  "zerofi",
    "obriQD1zbpyLz95G5n7nJe6a4DPjpFwa5XYPoNm113y":  "obricv2",
    "9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp": "humidifi",
    "AQU1FRd7papthgdrwPTTq5JacJh8YtwEXaBfKU3bTz45": "aquifier",
}

# Well-known open AMMs / aggregators — outside this study's scope
CLASSIC_AMM_PATTERNS = re.compile(
    r"raydium|orca|meteora|whirlpool|saber|aldrin|crema|cropper|"
    r"step|stepn|symmetry|invariant|lifinity|sencha|cykura|gooseFX|"
    r"sanctum|marinade|sol_strategies|"
    r"openbook|phoenix|serum|cykura|crema|"
    r"jupiter|jup_|pump\.fun|pumpswap|"
    r"penguin|mercurial|saros|atrix|dexlab|stabble|"
    r"perps|perp|drift|zeta|mango|01_exchange|cypher|"
    r"dynamic_bonding|fluxbeam|onesol|stakedex|fox|"
    r"^stable\b|^cropper\b|^token\s+swap",
    re.I,
)

# Heuristic: name contains these tokens => more likely closed-source prop AMM
PROP_LIKE_PATTERNS = re.compile(
    r"\bfi$|\bfiv\d|\b[A-Z]{2,}fi\b|"
    r"market.?maker|principal|opaque|"
    r"\bobric|\btessera|\balphaq|\bgoon|\bbison|\bsolfi|\bhumidi|\baquif|\bzero",
    re.I,
)


def fetch_jupiter():
    r = requests.get(JUP_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_account_meta(program_id: str) -> dict:
    """getAccount on a program returns metadata: executable, dataLen of program account."""
    try:
        r = requests.post(
            RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [program_id, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}}],
            },
            timeout=20,
        )
        val = (r.json().get("result") or {}).get("value")
        if not val:
            return {}
        return {
            "executable": val.get("executable"),
            "owner": val.get("owner"),
            "lamports": val.get("lamports"),
            "space": val.get("space"),
        }
    except Exception as e:
        return {"err": str(e)}


def count_program_accounts(program_id: str) -> int | None:
    """How many accounts does the program own? Cheap signal of activity."""
    try:
        r = requests.post(
            RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getProgramAccounts",
                "params": [
                    program_id,
                    {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}},
                ],
            },
            timeout=30,
        )
        res = r.json().get("result")
        if isinstance(res, list):
            return len(res)
        return None
    except Exception:
        return None


def classify(prog_id: str, label: str) -> str:
    if prog_id in KNOWN_PAMMS:
        return "known_pamm"
    if CLASSIC_AMM_PATTERNS.search(label):
        return "classic_amm"
    if PROP_LIKE_PATTERNS.search(label):
        return "candidate_new_pamm"
    return "uncategorized"


def main():
    print(f"Fetching {JUP_URL}")
    labels = fetch_jupiter()
    print(f"  -> {len(labels)} programs")

    buckets: dict[str, list[dict]] = {
        "known_pamm": [],
        "candidate_new_pamm": [],
        "classic_amm": [],
        "uncategorized": [],
    }
    for prog, label in sorted(labels.items(), key=lambda kv: kv[1].lower()):
        buckets[classify(prog, label)].append({"program": prog, "label": label})

    print(f"\n=== Bucket sizes ===")
    for k, v in buckets.items():
        print(f"  {k:20s} {len(v)}")

    print(f"\n=== Candidate new prop AMMs (heuristic) ===")
    for c in buckets["candidate_new_pamm"]:
        print(f"  {c['label']:30s} {c['program']}")

    print(f"\n=== Uncategorized (worth a manual look) ===")
    for c in buckets["uncategorized"]:
        print(f"  {c['label']:30s} {c['program']}")

    # For uncategorized and candidates, fetch cheap on-chain signals
    print(f"\n=== On-chain signals for non-classic non-known programs ===")
    enrich_targets = buckets["candidate_new_pamm"] + buckets["uncategorized"]
    for c in enrich_targets:
        meta = fetch_account_meta(c["program"])
        n_accts = count_program_accounts(c["program"])
        c["account_count"] = n_accts
        c["program_meta"] = meta
        print(f"  {c['label']:30s} program_size={meta.get('space')}  accounts={n_accts}")
        time.sleep(0.4)

    out_path = os.path.join(os.path.dirname(__file__), "discovered_pamms.json")
    with open(out_path, "w") as f:
        json.dump(
            {
                "n_total": len(labels),
                "buckets": buckets,
                "known_pamms_in_brief": KNOWN_PAMMS,
            },
            f,
            indent=2,
        )
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
