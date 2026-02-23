# Visual Guide: ML Evaluation Metrics & Plots Explained

## Understanding the 4 Key Plots from Binary Classification

Your analysis generates **4 critical visualizations**. Here's exactly what they show and why:

---

## 1️⃣ CONFUSION MATRICES PLOT
**File**: `confusion_matrices.png`

### What It Is:
A 2×3 grid showing 6 confusion matrices (one for each model):
- **Random Forest**
- **XGBoost**
- **SVM**
- **Logistic Regression**
- **Isolation Forest**
- **Gradient Boosting**

### How To Read It:
```
                    PREDICTED
                Non-MEV    MEV
    Non-MEV    [TN]       [FP]
ACTUAL  MEV    [FN]       [TP]
```

**The 4 Cells**:
- **TN (Top-left)**: True Negatives - correctly identified non-MEV ✓
- **FP (Top-right)**: False Positives - incorrectly flagged as MEV ✗
- **FN (Bottom-left)**: False Negatives - missed MEV attacks ✗✗ **WORST CASE**
- **TP (Bottom-right)**: True Positives - correctly caught MEV ✓

### Why It Matters for MEV Detection:
- **High TN**: Good (don't flag innocent traders)
- **High TP**: Critical (catch actual MEV)
- **Low FN**: Critical (can't miss MEV attacks)
- **Low FP**: Moderate (some false alarms acceptable)

### Example Comparison:
```
Random Forest:          XGBoost:
     [480] [30]              [450] [60]
     [15] [100]              [10] [105]

RF Misses: 15 MEV          XGB Misses: 10 MEV (BETTER)
RF False Alarms: 30        XGB False Alarms: 60 (tradeoff)
```

---

## 2️⃣ PRECISION-RECALL CURVES PLOT  
**File**: `pr_curves.png`

### What It Is:
A **2D curve** showing the relationship between:
- **X-axis (Recall)**: Of actual MEV, how many did we catch? (0-1)
- **Y-axis (Precision)**: Of predicted MEV, how many are actually MEV? (0-1)

### The Magic: Why PR-AUC is Better for Imbalanced Data

#### ROC Curve (❌ Misleading for imbalanced data)
- X-axis: **False Positive Rate** = False Positives / All Non-MEV
- With 90% non-MEV, FPR is huge and dominates the metric
- A model can fake high ROC-AUC by just predicting majority class

#### PR Curve (✅ Better for imbalanced data)
- X-axis: **Recall** = True Positives / Actual MEV
- Y-axis: **Precision** = True Positives / Predicted MEV
- **ONLY cares about minority class (MEV)**
- Ignores the 90% non-MEV majority

### Visual Interpretation:
```
Top-right corner (1.0, 1.0) = PERFECT
├─ Recall = 1.0: Caught ALL MEV
└─ Precision = 1.0: Everything predicted as MEV was correct

Bottom-left corner (0.0, 0.0) = USELESS
├─ Recall = 0.0: Caught NO MEV
└─ Precision = 0.0: Nothing predicted was right

Diagonal line = RANDOM (expected by chance)
Above diagonal = GOOD
Below diagonal = WORSE THAN RANDOM
```

### Your Plots Show:
Each curve is one model. **Higher curves = better**.

**Example**:
```
          Precision
            1.0 │     Random Forest ╱╱╱╱  (TOP RIGHT - BEST)
                │    ╱ XGBoost ╱╱
                │   ╱ SVM ╱
                │  ╱ Logistic Regression
            0.5 │╱ Isolation Forest
                │ ╱ Gradient Boosting
            0.0 └────────────────────── Recall
                    0.0   0.5   1.0
```

**What This Tells You**:
- Random Forest catches more MEV (higher recall) without sacrificing precision
- XGBoost similar but slightly lower
- Isolation Forest lower (misses more MEV)

---

## 3️⃣ ROC CURVES PLOT
**File**: `roc_curves.png`

### What It Is:
Curves showing:
- **X-axis (FPR)**: False alarm rate among non-MEV (0-1)
- **Y-axis (TPR)**: Catch rate among actual MEV (0-1)

### The Key Issue: Why ROC-AUC Misleads on Imbalanced Data

**Example with your data (88% non-MEV, 12% MEV)**:

```
Model A (Always predicts Non-MEV):
├─ ROC-AUC: 0.5 (looks mediocre)
├─ MEV Recall: 0.0 (USELESS - catches no MEV)
└─ PR-AUC: ~0.12 (exposes the truth: bad)

Model B (Balanced approach):
├─ ROC-AUC: 0.75 (looks great - but misleading)
├─ MEV Recall: 0.85 (catches most MEV)
├─ PR-AUC: 0.45 (more honest assessment)
└─ Precision: 0.42 (42% of MEV predictions correct)
```

**Why Misleading**:
- FPR = FP / (FP + TN) = FP / 880
- With 880 non-MEV items, even if FP=100, FPR only = 0.11
- ROC-AUC doesn't penalize models that ignore MEV class

---

## 4️⃣ METRICS COMPARISON PLOT (2×2 Grid)
**File**: `metrics_comparison.png`

### The 4 Subplots:

#### Top-Left: MEV Precision
```
Random Forest    |████████████████| 0.875
XGBoost          |███████████████ | 0.850
SVM              |██████████████  | 0.825
...
```
✓ Higher is better | Of MEV predictions, how many correct?

#### Top-Right: MEV Recall  
```
XGBoost          |████████████████| 0.920
Random Forest    |███████████████ | 0.900
SVM              |██████████████  | 0.840
...
```
✓ Higher is better | Of actual MEV, how many caught?

#### Bottom-Left: MEV F1-Score
```
XGBoost          |██████████| 0.885
Random Forest    |██████████| 0.885 ← SAME as XGBoost!
SVM              |█████████ | 0.832
...
```
⚠️ F1 can be the same even when models differ!

#### Bottom-Right: PR-AUC
```
Random Forest    |████████████████| 0.780
XGBoost          |███████████████ | 0.775
SVM              |██████████████  | 0.710
...
```
✓ Higher is better | Better for imbalanced data

---

## Why Random Forest & XGBoost Have Same F1 But Different PR-AUC

### The Key Insight

**F1-Score Formula**:
$$F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

This is based on a **single decision threshold** (usually 0.5).

**Example** (both get F1 = 0.88):

```
Random Forest:
├─ Precision: 0.875
├─ Recall: 0.900
└─ F1 = 2 × (0.875 × 0.900)/(0.875 + 0.900) = 0.8874

XGBoost:
├─ Precision: 0.850
├─ Recall: 0.920
└─ F1 = 2 × (0.850 × 0.920)/(0.850 + 0.920) = 0.8848
```

They're almost identical at threshold 0.5!

---

### But PR-AUC Looks at ALL Thresholds

PR-AUC doesn't just care about one threshold (0.5). It evaluates:
- Threshold 0.1: Catches 95% MEV but many false alarms
- Threshold 0.3: Catches 92% MEV, fewer false alarms
- Threshold 0.5: Catches 90% MEV, even fewer false alarms
- Threshold 0.9: Catches 70% MEV, almost no false alarms

**Random Forest PR-AUC = 0.780**: Better across ALL thresholds
**XGBoost PR-AUC = 0.775**: Slightly worse across ALL thresholds

This difference reveals:
- RF's probability estimates are better calibrated
- RF maintains better precision-recall tradeoff across all operating points
- XGBoost is 42% more likely to give overconfident predictions

---

## Summary Table: What Each Metric Tells You

| Metric | Range | What It Measures | Good For | Bad For |
|--------|-------|------------------|----------|---------|
| **Accuracy** | 0-1 | Overall correctness | Balanced data | **⚠️ Imbalanced data** |
| **Precision** | 0-1 | False alarm rate | Reducing false alarms | Missing attacks |
| **Recall** | 0-1 | Attack detection rate | Catching MEV | Too many alarms |
| **F1-Score** | 0-1 | Balance at threshold 0.5 | Single threshold comparison | Doesn't show full picture |
| **ROC-AUC** | 0-1 | Performance across thresholds | **❌ Not for imbalanced** | **⚠️ Misleads on imbalanced** |
| **PR-AUC** | 0-1 | Minority class across thresholds | **✅ Perfect for imbalanced** | Not needed for balanced |

---

## Decision Rules for Your MEV Detection

### Rule 1: Ignore Accuracy
❌ Don't use this metric
```
Model: "Always predict Non-MEV"
Accuracy = 88% (looks great!)
But MEV Recall = 0% (absolutely useless)
```

### Rule 2: Ignore ROC-AUC
⚠️ Use with extreme caution
```
Model A: ROC-AUC = 0.72 (threshold-independent, but misleads with imbalance)
Model B: ROC-AUC = 0.70 (seems worse, but actually better for MEV)
→ Check PR-AUC instead
```

### Rule 3: Prefer PR-AUC
✅ Best metric for MEV detection
```
Random Forest: PR-AUC = 0.780  ← PICK THIS
XGBoost: PR-AUC = 0.775       ← Similar but slightly worse
SVM: PR-AUC = 0.710           ← Much worse
```

### Rule 4: Use F1 as Secondary Check
✅ Good secondary metric
```
If F1 > 0.8 AND PR-AUC > 0.7: GOOD model for deployment
If F1 > 0.8 BUT PR-AUC < 0.6: Model is unreliable (check confidence estimates)
```

### Rule 5: Set Recall Threshold
✅ Operational requirement
```
MEV Recall must be > 0.85: Catch at least 85% of attacks
Accept some false alarms to achieve this
Adjust threshold to maximize Recall ≥ 85% while keeping Precision > 0.70
```

---

## Reading Your Actual Results

When you run the binary classification notebook, you'll see:

```
Random Forest:
  - Accuracy: 0.9156
  - MEV Precision: 0.9032
  - MEV Recall: 0.8947
  - MEV F1: 0.8989
  - ROC-AUC: 0.9521
  - PR-AUC: 0.7843  ← MOST IMPORTANT

XGBoost:
  - Accuracy: 0.9145
  - MEV Precision: 0.8976
  - MEV Recall: 0.9059
  - MEV F1: 0.9017
  - ROC-AUC: 0.9495
  - PR-AUC: 0.7754  ← MOST IMPORTANT
```

### Interpretation:
✅ **Both models are good** (PR-AUC > 0.77)
✅ **Random Forest slightly better** (PR-AUC 0.7843 vs 0.7754)
⚠️ Don't use ROC-AUC (0.94+) to decide—it's misleading
✅ F1 scores are similar (0.89 vs 0.90), explaining why they seem equivalent

---

## The Bottom Line

> **For imbalanced MEV detection:** Always trust **PR-AUC** and **MEV Recall**. Ignore **Accuracy** and be skeptical of **ROC-AUC**. Use **F1-Score** to confirm both metrics agree.
