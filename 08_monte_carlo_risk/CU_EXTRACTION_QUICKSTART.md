# 🚀 CU Benchmark Workflow: Quick Start

This directory contains everything you need to measure Compute Unit (CU) consumption in your Prop AMM and generate the professional CU Percentile Heatmap.

---

## 📋 What You Have

### 1. **CU_MEASUREMENT_GUIDE.md** 📖
Comprehensive guide explaining:
- What CU is and why it matters
- How different operations cost differently
- Where to find CU data in Solana
- Common measurement pitfalls

**Read this first to understand the context.**

---

### 2. **Three Data Collection Scripts**

#### **Option A: `simulate_cu_benchmark.py`** ⚡ (START HERE)
**Best for: Testing the heatmap workflow immediately**

Generates realistic synthetic CU data for all 14 operations.

```bash
# Quick test (5 minutes)
python simulate_cu_benchmark.py --samples 100 --output outputs/cu_benchmark_logs.csv

# Full dataset (production-quality simulation)
python simulate_cu_benchmark.py --samples 500 --output outputs/cu_benchmark_logs.csv
```

**Output**: `outputs/cu_benchmark_logs.csv` ready for heatmap

---

#### **Option B: `extract_cu_from_rpc.py`** 🔗 (PRODUCTION DATA)
**Best for: Collecting real CU data from your deployed program**

Queries Solana RPC to extract CU metrics from live transactions.

```bash
# Requires your program ID
python extract_cu_from_rpc.py \
  --program YOUR_PROGRAM_ID \
  --limit 1000 \
  --output outputs/cu_benchmark_logs.csv

# Specify mainnet or devnet
python extract_cu_from_rpc.py \
  --program YOUR_PROGRAM_ID \
  --rpc https://api.mainnet-beta.solana.com \
  --limit 5000
```

**Requirements**:
```bash
pip install solders httpx pandas
```

**Output**: Real CU data from your program

---

#### **Option C: `extract_cu_from_logs.py`** 📄 (FROM FILES)
**Best for: If you already have logs or exported data**

Parses Solana logs or CSV files to extract CU values.

```bash
# Parse Solana log file
python extract_cu_from_logs.py \
  --logfile solana_logs.txt \
  --output outputs/cu_benchmark_logs.csv

# Parse existing CSV with CU data
python extract_cu_from_logs.py \
  --csv validator_logs.csv \
  --cu-column compute_units \
  --output outputs/cu_benchmark_logs.csv
```

---

### 3. **CU_PERCENTILE_HEATMAP.ipynb** 📊
Jupyter notebook that:
- Loads CU benchmark data
- Computes percentiles (min, p50, p75, p90, p95, p99, max)
- Generates professional YlOrRd heatmap visualization
- Identifies dangerous operations (p99 > 30k CU)
- Exports results (PNG, JSON, CSV)

---

## 🎯 Quick Start Workflow

### Step 1: Choose Your Data Source (Pick ONE)

**If you want to test immediately:**
```bash
python simulate_cu_benchmark.py --samples 500
```

**If you have a deployed program:**
```bash
python extract_cu_from_rpc.py --program YOUR_PROGRAM_ID --limit 1000
```

**If you have existing logs/CSV:**
```bash
python extract_cu_from_logs.py --logfile your_logs.txt
# or
python extract_cu_from_logs.py --csv your_data.csv --cu-column compute_units
```

---

### Step 2: Verify the Output

Check that `outputs/cu_benchmark_logs.csv` was created:
```bash
ls -lh outputs/cu_benchmark_logs.csv

# Preview the data
head -20 outputs/cu_benchmark_logs.csv
```

Expected columns:
```
operation,cu,timestamp,slot,tx_hash,base_cu,remaining_cu
BlindUpdate / blindupdate,47,2026-02-25T...,12345678,sim_00001,45,
FastUpdate / all,125,2026-02-25T...,12345679,sim_00002,120,
Swap Buy / Curve C,29543,2026-02-25T...,12345680,sim_00003,29800,
...
```

---

### Step 3: Generate the Heatmap

Open `CU_PERCENTILE_HEATMAP.ipynb` and:

1. **Run Cell 1–2**: Import libraries and configure
2. **In Step 2 cell**: Update `data_path` if needed (or leave default)
3. **Run all cells**: Generates heatmap + analysis + exports

Output files:
- `outputs/images/cu_percentile_heatmap.png` — Professional visualization
- `outputs/cu_percentile_analysis.csv` — Spreadsheet-ready data
- `outputs/cu_percentile_analysis.json` — Structured results

---

## 📊 Expected Output

### Heatmap Visualization
Shows all 14 operations with CU percentiles:
- **Yellow** = Safe (< 10k CU)
- **Orange** = Caution (10k–30k CU)
- **Dark Red** = Danger (> 30k CU, likely fails on-chain)

### Summary Table
```
                            min      p50      p75      p90      p95      p99      max
BlindUpdate / blindupdate    30       47       52       61       72      105      240
FastUpdate / all             75      120      142      162      188      240      489
Swap Buy / Curve C       18,456   29,800   38,400   49,200   58,300   64,200   87,900
...
```

### Safety Analysis
```
✓ Safe operations (p99 < 20k):    10/14
⚠  Caution zone (20k–30k):         3/14
❌ Danger zone (> 30k):             1/14
```

---

## 🔍 Troubleshooting

### "No CU data found"
- **Cause**: CSV column names don't match
- **Fix**: Check column names in your file:
  ```bash
  head -1 your_file.csv
  ```
  Update `data_path` in heatmap notebook or use `--cu-column` flag

### RPC connection timeout
- **Cause**: Network issue or invalid RPC URL
- **Fix**: Try a different RPC endpoint:
  ```bash
  python extract_cu_from_rpc.py \
    --program YOUR_ID \
    --rpc https://api.devnet.solana.com
  ```

### Operation names don't match expected format
- **Cause**: Log parsing inferred wrong operation type
- **Fix**: Manually edit CSV to fix operation names before running heatmap

### "Only 5 operations found (expected 14)"
- **Cause**: Your program doesn't emit all 14 operation types yet
- **Fix**: Either:
  - Use simulated data for testing: `python simulate_cu_benchmark.py`
  - Expand data collection window (more transactions = more operation types)

---

## 💡 Pro Tips

### 1. **Quick Testing Loop**
```bash
# Test the pipeline quickly
python simulate_cu_benchmark.py --samples 50 --output outputs/test_cu.csv

# Then run heatmap with test data
# (Update data_path in notebook to 'outputs/test_cu.csv')
```

### 2. **Compare Multiple Programs**
```bash
# Extract CU from Program A
python extract_cu_from_rpc.py --program PROGRAM_A_ID --output outputs/cu_program_a.csv

# Extract CU from Program B
python extract_cu_from_rpc.py --program PROGRAM_B_ID --output outputs/cu_program_b.csv

# Generate heatmaps for both
# (Update data_path in notebook for each)
```

### 3. **Track Optimization Progress**
```bash
# Before optimization
python extract_cu_from_rpc.py --program YOUR_ID --output outputs/cu_baseline.csv

# After optimization
python extract_cu_from_rpc.py --program YOUR_ID --output outputs/cu_optimized.csv

# Compare by changing data_path between runs
```

### 4. **Collect During Stress Test**
For most realistic p99 measurements:
```bash
# During high-volume period (network congestion)
python extract_cu_from_rpc.py \
  --program YOUR_ID \
  --limit 5000 \
  --output outputs/cu_stress_test.csv
```

---

## 📈 Challenge Integration

**For Prop AMM Challenge submission:**

1. **Collect mainnet data**:
   ```bash
   python extract_cu_from_rpc.py \
     --program YOUR_PROGRAM_ID \
     --rpc https://api.mainnet-beta.solana.com \
     --limit 10000 \
     --output outputs/cu_mainnet_final.csv
   ```

2. **Generate heatmap** with final data

3. **Export results**:
   - PNG for presentation
   - JSON for technical specs
   - CSV for spreadsheet

4. **Include in report**:
   - Show heatmap visualization
   - Highlight safety score
   - Document any danger zone mitigations

---

## 📚 File Reference

| File | Purpose | Status |
|------|---------|--------|
| `CU_MEASUREMENT_GUIDE.md` | Comprehensive documentation | ✅ Created |
| `simulate_cu_benchmark.py` | Generate synthetic data | ✅ Created |
| `extract_cu_from_rpc.py` | Extract from live program | ✅ Created |
| `extract_cu_from_logs.py` | Parse logs/CSV files | ✅ Created |
| `CU_PERCENTILE_HEATMAP.ipynb` | Generate visualization | ✅ Created |
| `CU_EXTRACTION_QUICKSTART.md` | This file | ✅ You are here |

---

## 🎯 Next Steps

### Immediate (Now):
- [ ] Read `CU_MEASUREMENT_GUIDE.md`
- [ ] Run `simulate_cu_benchmark.py` to test pipeline
- [ ] Open `CU_PERCENTILE_HEATMAP.ipynb`
- [ ] Generate test heatmap

### Short-term (This week):
- [ ] Identify where your real CU data is
- [ ] Use appropriate extraction script (RPC / logs / CSV)
- [ ] Generate production heatmap
- [ ] Analyze results

### Long-term (Before submission):
- [ ] Collect mainnet CU data
- [ ] Optimize any danger zone operations
- [ ] Generate final heatmap
- [ ] Include in challenge report

---

## ❓ Questions?

Refer to:
1. **"How do I measure CU?"** → `CU_MEASUREMENT_GUIDE.md` Section 2–3
2. **"How do I use the scripts?"** → Script docstrings (`python script.py --help`)
3. **"Why is my data missing?"** → `CU_MEASUREMENT_GUIDE.md` Section 7 (pitfalls)
4. **"How do I interpret the heatmap?"** → Notebook cells 5–6

---

**Happy profiling! 🚀 Let's crush the CU leaderboard!**
