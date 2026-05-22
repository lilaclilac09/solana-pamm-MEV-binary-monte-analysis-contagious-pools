# Solana Prop AMM Pool Layout: Methodology Audit + Extensions

> Borrows methodology from `PAMM_RESEARCH_BRIEF.md` (gist by mubarizkyc).
> All 10 PAMMs are **closed-source Rust** programs — source-code analysis is not
> available; on-chain account inspection is the only path.
> Date: 2026-05-22

## What this folder contains

| File | Purpose |
|---|---|
| `verify_brief_offsets.py` | Validates the brief's published (mint1, mint2) byte offsets against live on-chain data |
| `inspect_humidifi_pool.py` | Hex dump + cross-pool diff for one PAMM's accounts (template for any closed-source PAMM) |
| `reverse_humidifi_mint_offset.py` | Searches for known SPL mint bytes inside HumidiFi pool accounts |
| `derive_humidifi_pool_mints.py` | Recovers (pool → mint pair) via swap-tx `postTokenBalances` |
| `derive_humidifi_mints_minimal.py` | Minimal single-tx-per-pool version (cheap RPC) |
| `derive_humidifi_mints_retry.py` | Re-resolves pools whose latest tx wasn't a swap |
| `brief_offsets_verification.json` | Live verdict for each of the brief's 8 offsets |
| `humidifi_pool_mints.json` | (pool, mint1, mint2) table for HumidiFi (brief had no offsets) |
| `HUMIDIFI_REVERSE_ENGINEERING.md` | Detailed reverse-engineering notes for HumidiFi specifically |

## Finding 1 — Brief's 8 offsets are real (validated live)

Ran `verify_brief_offsets.py` against 5 random pools per PAMM:

| PAMM | size | (m1, m2) | verdict | known base mint hits |
|---|---|---|---|---|
| bisonfi  | 2048 | 184/216 | ✅ GOOD | (per pool) |
| tessera  | 1264 | 56/24 | ✅ GOOD | (per pool) |
| alphaQ   | 672  | 272/240 | ✅ GOOD | (per pool) |
| solfi    | 2800 | 2696/2664 | ✅ GOOD | 8/10 hits SOL/USDC/USDT |
| solfiv2  | 1728 | 88/56 | ✅ GOOD | 9/10 |
| goonfiv2 | 2048 | 112/80 | ✅ GOOD | 8/10 |
| zerofi   | 7456 | 104/72 | ✅ GOOD | 7/10 |
| obricv2  | 666  | 202/234 | ✅ GOOD | 10/10 |

→ The brief's reverse-engineering work is reproducible and load-bearing.
Direct quotation of the table is safe for downstream tools.

## Finding 2 — HumidiFi is structurally different

> Brief explicitly noted "humidifi … no offsets given, need to reverse yourself."
> Result: **there ARE no offsets to find.**

Evidence (`inspect_humidifi_pool.py` + `reverse_humidifi_mint_offset.py`):

- All 89 HumidiFi accounts are size **1728** — no separate mint-registry class
- Cross-pool byte diff: **1562 bytes identical**, 166 bytes vary
- The 443-byte block `[5:447]` is **identical** across every pool checked
- Scanning 12 pools for SOL/USDC/USDT/JTO/JLP/PYUSD/USD1/TOKEN_PROGRAM bytes: **zero hits**
- Header pattern looks packed/encoded:
  `XX 5a YY 7c ZZ 6f WW 96` repeats with bytes [1,3,5,7] = constant `5a 7c 6f 96`

**HumidiFi pool accounts do not store mint pubkeys anywhere.** They are opaque
pricing slots; mints are passed in at swap time. Any offset-based tool produces
incomplete data for HumidiFi.

## Finding 3 — Tx-based method recovers HumidiFi pool↔mint mapping

`derive_humidifi_mints_minimal.py` algorithm:

1. `getProgramAccounts(HUMIDIFI, dataSize=1728)` → pool pubkeys
2. For each pool: `getSignaturesForAddress(pool, limit=8)` (deeper if needed)
3. Walk signatures; for each: `getTransaction(sig, encoding=jsonParsed)`
4. First tx with non-empty `meta.postTokenBalances` → its 2 mints = pool pair
5. Skip tx without token balances (oracle updates, admin calls)

Sample of resolved pools (top-lamports HumidiFi pools, public RPC):

| Pool | Mint A | Mint B | Pair |
|---|---|---|---|
| `8sKQHfj…CCPu` | USDC | SOL | USDC/SOL |
| `DB3sUCP…oRwW` | USDC | SOL | USDC/SOL |
| `5dhYayH…BfD9` | USD1 | SOL | USD1/SOL |
| `6n9VhCw…WHuQ` | USDC | SOL | USDC/SOL |
| `AYZ1amn…cdUM` | USDC | ORE | USDC/ORE |
| `H3TyE2Q…WqMH` | USDC | `98sMhvDw…Mh5g` | USDC / unknown memecoin |

→ HumidiFi top pools are SOL/USDC-denominated, plus one yield-token (ORE) and
at least one memecoin lane. This matches the 16,828 fat-sandwich count: SOL/USDC
flow is the highest-volume MEV surface.

## Finding 4 — Method generalizes to any opaque PAMM

The brief's offset method assumes pool accounts store mint refs in plaintext.
HumidiFi breaks this. For any PAMM where the offset method fails (likely
**Aquifier** too — brief also omitted it), use the tx-based fallback:

```
discovery method = (
    offset-based   if  pool account contains mint bytes,
    tx-based       otherwise
)
```

Both methods produce the same `(pool, mint1, mint2)` table; the offset method
is cheaper (one RPC call per pool batch) but only works on AMMs that publish
mints in the account layout.

## Limitations encountered

- **Public Solana RPC** rate-limits aggressively (429) on `getSignaturesForAddress`
  and `getTransaction`. Production runs need Helius / Ironforge / QuickNode.
- 6/12 sampled HumidiFi pools had a non-swap latest tx; deeper sig lookback (20
  sigs) recovers most of them. Truly inactive pools (no swap in 1000+ sigs)
  match the brief's 24h-activity exclusion criterion (`Δslot < 216000`).
- HumidiFi's `[448:543]` 96-byte state region remains unparsed — next research
  target (reserves + oracle price encoding).

## Reproduction

```bash
# All scripts read SOLANA_RPC_URL; falls back to api.mainnet-beta.solana.com.
export SOLANA_RPC_URL='<your-paid-rpc>'   # recommended

python3 06_pool_analysis/verify_brief_offsets.py             # confirms brief's 8 offsets
python3 06_pool_analysis/inspect_humidifi_pool.py            # confirms HumidiFi has no mint bytes
python3 06_pool_analysis/derive_humidifi_mints_minimal.py    # builds (pool, mints) table
python3 06_pool_analysis/derive_humidifi_mints_retry.py      # re-tries empty pools
```

## What this unblocks in the broader project

1. Every HumidiFi MEV event in `02_mev_detection/per_pamm_all_mev_with_validator.csv`
   can now be tagged with its token pair via `humidifi_pool_mints.json`.
2. `05_token_pair_analysis` can join across all 8 PAMMs uniformly (offset or tx
   method, same output schema).
3. `13_mev_comprehensive_analysis/CONTAGION_ANALYSIS.md` gains a token-pair
   dimension — currently only validator/attacker.
4. Method extends to discovering new PAMMs (brief's direction C) by templating
   the same diff-and-derive workflow.
