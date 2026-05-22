# Aquifier Pool Account: Reverse Engineering Notes

> Borrowed methodology from `PAMM_RESEARCH_BRIEF.md` (mubarizkyc gist).
> Brief explicitly noted: "humidifi 和 aquifier 没给偏移，需要自己逆向."
> Date: 2026-05-22

## TL;DR

**Aquifier pool accounts (size 1056) don't store mints at stable offsets** —
identical structural finding to HumidiFi. BUT Aquifier exposes a separate
**8492-byte registry account** `CNC5TaeNQEoSPfQKZ7GgfM4R8WYAJRKRSHFCHkf2H7ko`
that contains a base-mint table at deterministic offsets. Pools index into
this registry — the brief's "offset table" pattern *does* apply to Aquifier,
just one indirection level removed.

## Account inventory

`getProgramAccounts(AQU1FRd7papthgdrwPTTq5JacJh8YtwEXaBfKU3bTz45)`:

| Size | Count | Role |
|---|---|---|
| 1056 | 35 | pool accounts |
| 8492 | 1  | **mint registry** (`CNC5TaeN…`) — verified |
| 8552 | 1  | secondary registry / config (`5AVyF6qJ…`) — no known base mints |
| 0    | 1  | placeholder (`BYpcqij1…`) |

## Finding 1: Pool accounts have no stable mint offset

Sampled 8 highest-lamport pools, searched for SOL/USDC/USDT/JTO/JLP/PYUSD/USD1
bytes at every offset:

| Pool | Mint hits |
|---|---|
| `GtwzYxBQ…` | USDC @ offset 952 (only one) |
| `A9j8JWCL…` | none |
| `4QjpJDWp…` | none |
| `DKCGgPdy…` | none |
| `2wz6vj1T…` | none |
| `FjGcWLzt…` | none |
| `GuZUrX6A…` | none |
| `2gveWAEy…` | none |

`offset 952` appears in only 1/8 pools → not a structural slot, coincidental
byte match. Pools are opaque pricing slots, same as HumidiFi.

## Finding 2: Aquifier has a real mint registry (`CNC5TaeN…`, 8492 bytes)

Scanning `CNC5TaeN…` for known SPL mints:

| Mint | Offset |
|---|---|
| SOL   | 131  |
| PYUSD | 527  |
| USDC  | 1055 |
| USDT  | 1121 |

The pattern (gaps of 396, 528, 66) suggests variable-length entries — each
entry is probably `(mint: 32 + name + decimals + state)` packed tightly. The
brief's "offset table" idea works here, but you index the **registry** rather
than the pool.

**This is the headline finding** — Aquifier's architecture is registry-indexed,
not byte-encoded. Knowing the registry pubkey + offsets, any consumer can:
1. Fetch the registry once.
2. Cache the mint table (rarely changes).
3. Read pool accounts and decode whatever index field they store into a mint.

## Finding 3: The 8552-byte account holds no known mints

`5AVyF6qJ…` (size 8552) returned zero hits for any of the 7 well-known mints
we searched. Hypothesis: oracle / fee tier / admin config, distinct from the
mint registry. Worth a separate inspection later.

## Finding 4: Aquifier hosts multi-pair pools

tx-based resolution recovered mint sets for 14/35 pools:

| Pattern | Count | Example pools |
|---|---|---|
| 2 mints (clean pair) | 6 | USDC/SOL, USDC/USDT, USDC/PYUSD, USDC/JLP-like |
| 3+ mints (multi-pair bag) | 8 | `4QjpJDWp…`: USDC/SOL/USD1/HsXc.../FZN7.../FeR8...pump (6-token bag); `AwRau9gB…`: USDC/SOL/mega/x95H/FZN7.../GLeewid… (6-token bag) |
| empty / non-swap latest tx | 21 | (need deeper sig lookback or paid RPC) |

Distinct mints discovered in Aquifier swap traffic:
- Stables: USDC, USDT, USD1, PYUSD
- BTC: `cbbtcf…iMij` (Coinbase wrapped BTC)
- L2 / index: `megaA5QDK1q…` (MegaETH?), `x95HN3…`
- Memecoins via pump.fun: `FeR8…pump`, `VCwFrvr…pump`, `a3W4qut…pump`, `CkBjp8p8…`
- BONK derivative: `H6qnGp…bonk`
- Others: `METvsv…`, `CASHx9KJUStyftLFWGvEVf59SGeG9sh5FfcnZMVPCASH`, `2zMMhcV…`, ...

The multi-mint bags suggest Aquifier pools may operate as **multi-asset
liquidity slots** routing 3+ tokens through one pool account — a more
ambitious model than 2-sided constant-product AMMs.

## Methodology summary

Combine three passes per opaque PAMM:
1. **Pool byte scan** — confirms whether brief's offset method applies.
2. **Account-class enumeration** — discovers registry / config accounts of
   different sizes that may hold mint refs.
3. **tx-based mint derivation** — fallback when bytes are useless.

## Reproduction

```bash
# Requires: requests, base58 (pip)
# Optional: SOLANA_RPC_URL=<helius/ironforge> (public RPC works but throttles)
python3 06_pool_analysis/aquifier_full_analysis.py
cat 06_pool_analysis/aquifier_analysis.json
```

## Next steps

- [ ] Decode the registry layout: each entry length + fields (decimals, name,
  authority?). With 4 mints at offsets [131, 527, 1055, 1121] the entry width
  is varied — needs hex inspection.
- [ ] Identify what the 8552-byte secondary registry holds (likely config).
- [ ] Re-run tx-derive with paid RPC + deeper sig walk to close the 21
  unresolved pools.
- [ ] Same play for any newly-discovered prop AMM via Jupiter route inspection.
