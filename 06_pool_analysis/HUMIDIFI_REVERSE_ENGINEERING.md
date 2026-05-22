# HumidiFi Pool Account: Reverse Engineering Notes

> Borrowed methodology from `PAMM_RESEARCH_BRIEF.md` (mubarizkyc gist), applied to HumidiFi.
> Brief explicitly noted: "humidifi and aquifier no offsets given, reverse it yourself."
> Date: 2026-05-22

## TL;DR

**HumidiFi pool accounts do not store mint pubkeys anywhere in their byte data.** The
brief's offset-based extraction method (`bytes[offset:offset+32]` → mint pubkey) is
structurally inapplicable. Mint pairs must be derived from swap transaction
`postTokenBalances`, not from `getAccountInfo`.

## Evidence

### 1. Single account size, low account count
`getProgramAccounts` on `9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp`:
- **89 accounts total**, **all size 1728**
- No secondary mint-registry account class

### 2. Account layout (per `inspect_humidifi_pool.py`)
Diff of two pools (`8sKQHfj…` vs `AvGeFw71…`) — 1562 same bytes, 166 different:

| Region | Bytes | Type | Notes |
|---|---|---|---|
| `[0:5]` | 5 | varies per pool | possibly per-pool nonce/version |
| `[5:447]` | **443** | **identical across pools** | shared structural config |
| `[448:543]` | 96 | varies | likely reserves / oracle / price state |
| `[544:567]` | 24 | identical | structural |
| `[568:688]` | mostly varies | per-pool tunables (fees / curve params?) |
| `[689:799]` | 111 | identical | structural |
| `[800:801]` | 2 | varies | small state |
| `[802:1727]` | **926** | **identical across pools** | shared post-tail config / padding |

### 3. No SPL token program references
Scan with `06_pool_analysis/inspect_humidifi_pool.py`:
```
TOKEN_PROGRAM      -- not found
TOKEN_2022         -- not found
ASSOCIATED_TOKEN   -- not found
PROGRAM_ITSELF     -- not found
```
The only hit for `SYSTEM_PROGRAM` is a long run of zero bytes (false positive: system
program pubkey = 32 zero bytes).

### 4. No well-known mint bytes
Scan with `06_pool_analysis/reverse_humidifi_mint_offset.py` across 12 pools for SOL,
USDC, USDT, JTO, JLP, PYUSD, USD1: **zero hits at any offset**.

### 5. Header pattern looks obfuscated
First 64 bytes of pool `8sKQHfj…`:
```
0000  14 ee da 0a 87 90 d1 69 2c 5a 13 7c 38 6f 2f 96
0010  2d 5a 10 7c 3b 6f 2c 16 2e 5a 11 7c 3a 6f 2d 96
0020  2c 5a 16 7c 3d 6f 2a 96 28 5a 17 7c 3c 6f 2b 96
0030  ee 11 23 f5 7e 6f 28 96 2a 5a 15 7c 3e 6f 29 96
```
Bytes `[1, 3, 5, 7]` of each 8-byte cell are nearly constant (`5a 7c 6f 96`), with
small-range variation in bytes `[0, 2, 4, 6]`. Looks like packed/encoded data, not
raw pubkeys.

## Why this matters for the research

The brief frames "find the mint offset" as the universal pattern for all 10 prop AMMs.
HumidiFi (the highest-volume PAMM in our dataset — 16,828 fat sandwiches, 75 SOL net
profit, ~60% of total MEV) **breaks this pattern**. This is a methodological finding,
not a bug:

- HumidiFi seems to use a **principal-vault model**: pool accounts are opaque pricing
  slots, and the swap instruction passes both mints as accounts at swap time.
- Mint↔pool mapping is *only* discoverable from on-chain swap traces.
- Any tool that relies on `getProgramAccounts + offset slice` (the brief's pattern)
  will produce **incomplete data** for HumidiFi and possibly Aquifier.

## Working method: derive mints from swap tx

See `derive_humidifi_pool_mints.py`. Algorithm:

1. `getProgramAccounts(HUMIDIFI)` → pool pubkeys
2. For each pool: `getSignaturesForAddress(pool, limit=5)`
3. For each sig: `getTransaction(sig, encoding=jsonParsed)`
4. Collect mints in `meta.postTokenBalances` ∪ `meta.preTokenBalances`
5. Mint pair = top-2 mints appearing in ≥ ½ of sampled txs (filter out gas/fee tokens)

This produces a `(pool, mint1, mint2)` table that the brief's offset method cannot.

## Reproduction

```bash
# Requires: requests, base58 (pip)
python3 06_pool_analysis/inspect_humidifi_pool.py        # confirms no mint bytes
python3 06_pool_analysis/reverse_humidifi_mint_offset.py # confirms no offsets work
python3 06_pool_analysis/derive_humidifi_pool_mints.py   # produces pool->mints map
```

Optional env: `SOLANA_RPC_URL=<your-rpc>` — public mainnet works for these endpoints
but rate-limits after ~30 calls. For sustained scans use Ironforge / Helius.

## Next steps

- [ ] Apply same `derive_*_pool_mints.py` pattern to Aquifier (brief also missing).
- [ ] Once `(pool, mint1, mint2)` table is built, join into `02_mev_detection/per_pamm_*.csv` to give every HumidiFi MEV event a token-pair label.
- [ ] Investigate `[448:543]` state region for reserve / price encoding (next research target after mint mapping is settled).
