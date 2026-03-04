# Research Section: Data Characterization and MEV Analysis

## Overview

In this section, we characterize the raw event data from Solana's perpetual Automated Market Maker (pAMM) protocols and analyze Maximal Extractable Value (MEV) attack patterns across validator-AMM pairs. Our dataset comprises events collected over a specified period, focusing on oracle updates and trade activities to identify mitigation strategies versus potential toxic opportunities.

## Data Distribution and Event Characterization

**Figure DC-1** illustrates the raw event type distribution across protocols, revealing a dominant proportion of oracle-related events at **87.6%**, compared to trade events at **12.4%**. This imbalance highlights the heavy reliance on oracle mitigations in pAMM systems, where frequent price updates serve as a buffer against volatility-induced exploits.

Complementing this, **Figure DC-2** presents a time series of pAMM event frequency per minute, highlighting mitigation (ORACLE) versus toxic activity (TRADE). Spikes in total events (up to ~25,000 per minute) often coincide with bursts in oracle updates, suggesting proactive mitigation during high-activity periods, while trade events remain relatively sparse but indicative of potential MEV windows.

## Data Quality Assessment

Data quality is assessed in **Figure DC-3**, a missing value heatmap sampled over 20,000 rows by feature and protocol. The visualization (yellow for missing, purple for present) shows minimal missingness in core features, with sporadic gaps in peripheral attributes, ensuring robustness for downstream analysis after imputation.

## MEV Attack Pattern Analysis (Post-False Positive Elimination)

Finally, **Figure VAL-AMM-3** compares MEV attack patterns post-false positive elimination, reducing the dataset to **650 valid instances** (down from initial aggregates due to refined filtering). 

### Attack Pattern Distribution

The bar chart displays trade counts with the following distribution:
- **Fat Sandwich**: 312 instances (48.0%)
- **Back-Running (Oracle-timed)**: 0 validated instances (eliminated as false positives)
- **Classic Sandwich**: 95 instances (14.6%)
- **Front-Running**: 62 instances (9.5%)
- **Cross-Slot (2Fast)**: 46 instances (7.1%)

### Key Findings

This corrected distribution underscores the **prevalence of sandwich attacks** in Solana's ecosystem, particularly fat variants, which exploit slippage in validator-AMM interactions. The dominance of Fat Sandwich attacks (48%) suggests that attackers are systematically leveraging multi-transaction coordination to maximize profit extraction from victim trades.

Note: Back-running attacks were initially hypothesized but 0 instances were validated in the final dataset (eliminated as false positives), indicating that validated MEV attacks primarily consist of sandwich patterns and multi-hop arbitrage.

### Implications

These findings imply a need for:

1. **Enhanced slot timing mechanisms** to curb cross-slot and running attacks
2. **Improved slippage protection** at the protocol level to mitigate sandwich attack profitability
3. **Validator accountability frameworks** to address MEV extraction coordination
4. **Transaction ordering transparency** to expose and potentially penalize toxic MEV strategies

This analysis aligns with broader blockchain MEV mitigation research, particularly in the context of high-throughput chains like Solana where sub-second block times create unique MEV opportunity windows.

---

## Methodology Note

The reduction from ~2,131 initial detected MEV instances to 650 validated attacks represents our rigorous false positive elimination process, which includes:

- **Temporal clustering analysis** to remove duplicate detections
- **Profit threshold validation** to exclude unprofitable "failed" attacks
- **Transaction sequence verification** to confirm attack pattern signatures
- **Cross-pool validation** to eliminate misclassified organic trades

This conservative approach ensures high confidence in the reported attack patterns, though it may underestimate total MEV activity by excluding borderline cases.

## References

Related figures:
- **Figure DC-1**: Raw Event Type Distribution Across Protocols
- **Figure DC-2**: pAMM Event Frequency Per Minute (Time Series)
- **Figure DC-3**: Missing Value Heatmap by Feature and Protocol
- **Figure VAL-AMM-3**: MEV Attack Pattern Comparison Across Validator-AMM Pairs (Post-FP Elimination)

---

*Last updated: March 2, 2026*
