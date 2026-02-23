# 07 Ml Classification

## Process

- Cell 1: filterwarnings; plt.savefig(save_path, dpi
- Cell 2: print
- Cell 4: slot_counts; slot_trade_counts; oracle_by_slot; print
- Cell 15: results_df; merge_cols; on; print
- Cell 16: calculate_mev_metrics; xgb_mev; svm_mev; lr_mev; rf_mev
- Cell 17: results_df.to_csv(full_results_path, index; summary_stats.to_csv(summary_path, index; mev_attackers.to_csv(mev_only_path, index; top_mev_export.to_csv(top_mev_path, index; print
- Cell 18: plt.savefig(attacker_viz_path, dpi; print
- Cell 24: print; save_path
- Cell 26: print
- Cell 27: locals
- Cell 28: gmm_mev_metrics; print

## Results

### Execution Outputs

1. ✓ Total records: 2,559
2. ✓ Total features: 9
3. ✓ Total classes: 4
4. ⚠️  Warning: SVM requires at least 2 classes, but only 1 class(es) found.
5. ⚠️  Warning: Logistic Regression requires at least 2 classes, but only 1 class(es) found.
6. ✓ Saved: derived/ml_results/model_comparison.png
7. ✓ Saved: derived/ml_results/confusion_matrices.png
8. ✓ Saved: derived/ml_results/gmm_analysis.png
9. ✓ Saved: derived/ml_results/feature_importance.png
10. ✓ Saved: derived/ml_results/gmm_clusters_2d.png
11. ✓ Saved: derived/ml_results/results_summary.json
12. All results saved to: derived/ml_results/

### Generated Files

- No output files found. Run the notebook to generate outputs.

