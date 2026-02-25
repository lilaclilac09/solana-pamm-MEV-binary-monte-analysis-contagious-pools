# 📊 CU Measurement Guide: Extracting Compute Unit Data from Your Prop AMM

**Goal**: Collect realistic CU consumption metrics for all 14 critical operations (3 updates × 4 scopes + 2 sides × 4 curves/mixed).

**Target Outcome**: `outputs/cu_benchmark_logs.csv` with structure:
```
operation,cu,timestamp,slot,tx_hash,base_cu,remaining_cu
```

---

## 1. Understanding CU Consumption in Solana Prop AMMs

### What is CU (Compute Unit)?
- **Atomic cost unit** for Solana transaction execution
- **1 CU ≈ CPU cycle equivalent**
- Hard limit: **1.4M CU per transaction** (soft limit ~1.2M for safety)
- **Effective safe limit for frequent ops: 50k–100k CU** (leaves room for stack + future calls)

### Why Measure?
- **p99 CU** determines if txs fail during volatility spikes
- **Different curves cost differently** (pricing logic complexity)
- **Updates must be cheap** (<100 CU) to spam them frequently
- **Swaps on mixed curves are most expensive** (classic pattern)

---

## 2. Where to Get CU Data

### **Method A: From Solana RPC Logs** ✅ EASIEST
Extract from transaction confirmation response:

```json
{
  "result": {
    "value": {
      "err": null,
      "logs": [
        "Program log: Starting AMM swap",
        "Program consumed X compute units"  // ← THIS LINE
      ],
      "unitsConsumed": 45230  // ← OR THIS FIELD (post-fix)
    },
    "context": {
      "slot": 123456789
    }
  }
}
```

**Tools to use:**
- `solana_rpc_client` (Rust)
- `solders` (Python)
- Raw HTTP to `getTransaction` RPC

---

### **Method B: From Binary Escrow Logs** (If you have them)
The flame graph you showed was from `quasar_escrow`:
```
quasar_escrow – CU Profile
├─ entrypoint: 93,969 CU
├─ parse: ↓20,977 CU
├─ make_escrow: [nested ops]
└─ refund, take, close: [branches]
```

---

### **Method C: Local Simulation on Anchor/Rust** 🔬
If you still have access to your program:

```bash
# Build with profiling enabled
anchor build --verifiable

# Run test harness that profiles each operation
cargo test --features "test-bpf"

# Extract from test output
```

---

## 3. Operations to Profile (14 Total)

### **Update Operations (6 types)**
| Operation | Scope | Expected CU | Notes |
|-----------|-------|-----------|-------|
| `BlindUpdate` | N/A | < 50 CU | Minimal state change |
| `FastUpdate` | all | < 150 CU | Quick oracle refresh |
| `FullUpdate` | oracle-only | < 500 CU | Just price feed |
| `FullUpdate` | bid-all | < 2k CU | All bid levels |
| `FullUpdate` | ask-all | < 2k CU | All ask levels |
| `FullUpdate` | both-all | < 3.5k CU | Bid + ask (most expensive) |

### **Swap Operations (8 types)**
| Curve | Side | Expected CU | Notes |
|-------|------|-----------|-------|
| Curve A | Buy | ~10k–15k CU | Linear pricing |
| Curve A | Sell | ~10k–15k CU | Simple logic |
| Curve B | Buy | ~15k–20k CU | More complex |
| Curve B | Sell | ~15k–20k CU | ~same cost |
| Curve C | Buy | ~25k–35k CU | Most expensive (polynomial?) |
| Curve C | Sell | ~25k–35k CU | Also expensive |
| Mixed | Buy | ~30k–40k CU | Multiple branches |
| Mixed | Sell | ~30k–40k CU | Most contagion risk |

---

## 4. Collection Strategy

### **Phase 1: Direct RPC Query** (Days 1–2)
**Best for: Already-deployed program (mainnet/devnet)**

#### Step 1: Connect to Network
```python
from solders.rpc.responses import GetTransactionResp
import httpx

# Point to your Prop AMM's transactions
# Mainnet: https://api.mainnet-beta.solana.com
# Devnet: https://api.devnet.solana.com
# Custom validator (e.g., Harmonic, Jito)

rpc_url = "https://api.mainnet-beta.solana.com"
```

#### Step 2: Query Recent Transactions
```python
# Find all txs to your program in last 100 slots
def get_program_txs(program_id: str, limit: int = 1000):
    """Query program txs and extract CU"""
    # Use getSignaturesForAddress → getTransaction pattern
    pass
```

#### Step 3: Filter by Operation Type
```python
def classify_operation(logs: list[str], instruction: dict) -> str:
    """
    Read logs + instruction data to infer operation:
    - "..parse..:make_escrow" → "Swap Buy / Curve B"
    - "..take" + small CU → "FastUpdate / all"
    - etc.
    """
    pass
```

---

### **Phase 2: Synthetic Simulation** (Days 3–5)
**Best for: Testing before mainnet**

Generate realistic CU data matching your program structure:

```python
import numpy as np

def simulate_cu_distribution(operation: str, base_cu: int, num_samples: int = 1000):
    """
    Simulate realistic CU with:
    - Base cost (constant)
    - Variable overhead (20–50% jitter)
    - Extreme spikes (1–5% of runs 2–3x higher)
    """
    # p50: base_cu
    # p90: base_cu * 1.3
    # p99: base_cu * 1.8
    # max: base_cu * 3
    pass
```

---

## 5. Data Collection Script Structure

### **Script 1: `extract_cu_from_rpc.py`**
Live extraction from validator RPC:
```python
# Step 1: Connect to RPC
# Step 2: Get all program signatures
# Step 3: For each tx:
#   - Fetch full transaction
#   - Extract CU (from logs or field)
#   - Parse instruction to get operation type
#   - Save to CSV
```

### **Script 2: `extract_cu_from_logs.py`**
Parse Solana log output (if you have files):
```python
# Step 1: Read solana logs
# Step 2: Parse each line for operation markers
# Step 3: Extract CU values
# Step 4: Aggregate and save
```

### **Script 3: `simulate_cu_benchmark.py`**
Generate synthetic data for testing:
```python
# Step 1: Define 14 operations
# Step 2: For each operation:
#   - Generate base CU
#   - Create distribution (1000 samples)
#   - Add percentiles
# Step 3: Save to CSV matching heatmap format
```

---

## 6. Validation Checklist

Before feeding data into the heatmap:

- [ ] **14 operations present**: All updates + all swaps
- [ ] **Multiple samples per operation**: ≥100 runs each  
- [ ] **Realistic distributions**: p99 < 2× p50 (or clearly document outliers)
- [ ] **Operation names match**: Exactly as in heatmap (`"Swap Buy / Curve C"`)
- [ ] **CU values in reasonable range**: 50–50k for updates, 10k–40k for swaps
- [ ] **No NaN/invalid values**: All rows complete
- [ ] **Percentiles make sense**: min ≤ p50 ≤ p99 ≤ max

---

## 7. Quick Reference: Common CU Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Only measuring average | Miss spikes (fail p99) | Collect **distributions**, not just avg |
| Single run per operation | Huge variance | **≥100 runs** per operation type |
| Ignoring validator type | Jito/Harmonic differ by 20–30% | Measure on **both** if submitting to challenge |
| Not sampling during volatility | Underestimate p99 | Run during **high-volume windows** |
| Mixing updates/swaps in logs | Wrong totals | **Parse instruction type first** |

---

## 8. Next Steps

### If you have a deployed program:
1. Use `extract_cu_from_rpc.py` (provided below)
2. Query last 1000–5000 txs
3. Filter by operation type
4. Save to `outputs/cu_benchmark_logs.csv`
5. Run heatmap notebook

### If you're still developing:
1. Use `simulate_cu_benchmark.py` (provided below)
2. Generate 100 samples per operation
3. Test heatmap workflow
4. Replace data when production txs available

### For challenge submission:
- Collect **mainnet data** during real trading (most realistic)
- Compare **Jito BAM** vs **Harmonic** separately (different costs)
- Document **validator used** in report

---

## References

- **Solana Docs**: https://docs.solana.com/developing/on-chain-programming/compute-budget
- **RPC Spec**: `getTransaction` method → `unitsConsumed` field
- **Escrow Profiling**: Look for `Program consumed X compute units` in tx logs
