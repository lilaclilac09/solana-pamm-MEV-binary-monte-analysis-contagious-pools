# PAMM Research Log — Round 3

Date: 2026-05-23
Following: #5 (PAMM offset methodology + HumidiFi), #6 (Aquifier registry discovery)

Three independent tracks landed in this PR:
1. **Discover new prop AMMs** beyond the brief's 10 — Jupiter program-id table diff.
2. **Decode the Aquifier registry layout** — 66-byte stride confirmed.
3. **Inspect HumidiFi state region [448:543]** — reserves / oracle slot extraction.

---

## 1. New PAMM discovery via Jupiter

`discover_new_pamms.py` pulls `https://lite-api.jup.ag/swap/v1/program-id-to-label`
(91 programs total) and classifies:

| Bucket | Count | Notes |
|---|---|---|
| `known_pamm` | 10 | the brief's set, already covered |
| `classic_amm` | 42 | Raydium / Orca / Meteora / Lifinity / Phoenix etc. — out of scope |
| `candidate_new_pamm` | **3** | regex match on "*Fi" suffix |
| `uncategorized` | **36** | opaque labels worth manual triage |

### Explicit "*Fi" candidates (top priority)

| Label | Program ID | Notes |
|---|---|---|
| LemmingsFi | `BQEJZUB4CzoT6UhRffoCkqCyqQNrCPCSGHcPEmsdbEsX` | 3 accounts — small, possibly experimental |
| TaurusFi   | `9VX8EKBg6vM6tA68xaDsPkbrx26XConZjkQmhVApUptc` | 5 accounts |
| Woofi      | `WooFif76YGRNjk1pA8wCsN67aQsD9f9iLsz4NcJ1AVb`   | acct count fetch failed |

### High-activity uncategorized candidates

These returned non-trivial program-account counts (small slice — most fetches hit RPC limits):

| Label | Program ID | Accounts |
|---|---|---|
| DefiTuna | `fUSioN9YKKSa3CUC2YUc4tPkHJ5Y6XW1yz8y6F7qWz9` | **2676** |
| Gavel    | `srAMMzfVHVAtgSJc8iH6CfKzuWuUTzLHVCE81QU1rgi` | 187 |
| Guacswap | `Gswppe6ERWKpUTXvRPfXdzHhiCyJvLadVvXGfdpBqcE1` | 123 |
| TaurusFi | (above) | 5 |
| LemmingsFi | (above) | 3 |

### Notable opaque labels (worth a manual look)

`Heaven`, `Obsidian`, `Riptide`, `Quantum`, `Scorch`, `Omnipair`, `Hylo Exchange`,
`Manifest`, `Boop.fun`, `Carrot`, `Voltr`, `WhaleStreet`, `Virtuals`, `Trends`,
`Scale Amm`, `Scale Vmm`, `MetaDAO`, `M Swap`, `Moonit`, `PancakeSwap`.

→ Saved to `discovered_pamms.json` for downstream filtering.

---

## 2. Aquifier registry layout decoded (66-byte stride)

Building on #6 (4 known mints found at irregular offsets), `decode_aquifier_registry.py`
hypothesized + confirmed a uniform stride.

**Registry `CNC5TaeNQEoSPfQKZ7GgfM4R8WYAJRKRSHFCHkf2H7ko` (8492 bytes)**:
- Header: bytes `[0:131]` (likely admin + discriminator + entry count)
- Entry array: 16 entries at offsets `131 + 66·k`, each `mint(32) + metadata(34)`
- Tail: bytes `[131 + 66·16 = 1187 : 8492]` = **7305 bytes** — could be reserves /
  oracle state / capacity slack. Open question.

### Decoded mint inventory (16 entries)

| # | Offset | Mint | Resolved name |
|---|---|---|---|
| 0 | 131 | `So111...11112` | **SOL** |
| 1 | 197 | `WETZjtprkDMCcUxPi9PfWnowMRZkiGGHDb9rABuRZ2U` | wrapped ETH variant? |
| 2 | 263 | `a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump` | pump memecoin |
| 3 | 329 | `cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij` | **cbBTC** |
| 4 | 395 | `inxKXw9V2NDZE7hDijzpJaKKUb97NEPJDTCEEiYg4yY` | unknown |
| 5 | 461 | `pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn` | pump.fun infra? |
| 6 | 527 | `2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo` | **PYUSD** |
| 7 | 593 | `2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv` | unknown |
| 8 | 659 | `6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN` | unknown (likely token) |
| 9 | 725 | `8Jx8AAHj86wbQgUTjGuj6GTTL5Ps3cqxKRTvpaJApump` | pump memecoin |
| 10 | 791 | `9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump` | pump memecoin |
| 11 | 857 | `BWsnyEa1XtsNRdgPaDoA1WVUonF7BBGZTd2zc72NQsWT` | unknown |
| 12 | 923 | `CrAr4RRJMBVwRsZtT62pEhfA9H5utymC2mVx8e7FreP2` | unknown |
| 13 | 989 | `Dfh5DzRgSvvCFDoYc2ciTkMrbDfRKybA4SoFbPmApump` | pump memecoin |
| 14 | 1055 | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | **USDC** |
| 15 | 1121 | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | **USDT** |

Brief #6 only surfaced 4 of these (SOL, PYUSD, USDC, USDT) because the scan
limited itself to a known-mints search list. The 66-byte stride scan recovers
**all 16** including 4 pump.fun memecoins + cbBTC + unknown variants.

### Secondary registry (`5AVyF6qJ…`, 8552 bytes)

Returned 310 plausible-pubkey hits at stride=8 (i.e., many overlapping windows
of nearby pubkeys). No known base mints. Likely a per-pool config / oracle map
keyed off the pool pubkey, not a mint list. Decoding this is a separate task.

---

## 3. HumidiFi state region [448:543] — NOT live state

(See `humidifi_state_region.py`, output in `humidifi_state_region_decoded.json`.)

Methodology: snapshot the 96-byte `[448:543]` window for 6 top-lamports HumidiFi
pools, sleep 90s (268 slots), snapshot again. Look for u64/u128 lanes that
changed = candidate state fields.

**Result: zero bytes changed in any of the 6 pools across the 90s gap.**
Every u64 lane delta = 0. Every u128 lane is identical snap1 == snap2.

This **rejects the original hypothesis** that `[448:543]` encodes reserves /
oracle / last-update-slot. The bytes look high-entropy (uniformly in the
10^18 range) — consistent with the obfuscated header pattern. Most likely
explanation:

- The pool account stores **frozen-once parameters** (curve coefficients,
  vault pubkey, fee tier, admin pubkey), not live state.
- Real reserves are in external **SPL token vault accounts** owned by a
  per-pool PDA; updates happen via SPL token transfers, not pool-account writes.
- This explains why the brief gave no offset for HumidiFi: even the "state
  region" identified by inter-pool diffs is actually inter-pool *config*
  diff, not intra-pool *state* tick.

Open follow-ups:
- Retry with a 30-minute gap on the most-traded pool to definitively confirm.
- Find the SPL vault PDAs by parsing one full swap tx (account list).
- Decode `[448:543]` as bit-packed config under the obfuscation mask
  (`5a 7c 6f 96` pattern) from the header bytes.

---

## Files

```
06_pool_analysis/
├── discover_new_pamms.py            # Jupiter program-id-to-label scraper + classifier
├── discovered_pamms.json            # 91 programs bucketed
├── decode_aquifier_registry.py      # 66-byte stride scan, all 16 mints decoded
├── aquifier_registry_decoded.json   # per-mint offsets + secondary registry sample
├── humidifi_state_region.py         # dual-snapshot u64/u128 lane decoder
├── humidifi_state_region_decoded.json
└── RESEARCH_LOG.md                  # this file
```

## What this unblocks

- **Aquifier**: full mint inventory now derivable from one RPC call to `CNC5TaeN…`.
  Future scripts can read `index → mint` instead of per-pool tx walks.
- **MEV scope expansion**: 3 explicit candidates (LemmingsFi/TaurusFi/Woofi) + a
  shortlist of 36 uncategorized programs ready for the same offset/registry/tx
  reverse-engineering playbook.
- **HumidiFi pricing**: lane-level u64 diffs identify which bytes of [448:543]
  are slot-encoded (last-update slot), reserves, or oracle price.
