# Cross-scenario generalisation (nextgen data)

| Key | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) |
|---|---|---|---|---|---|---|
| Urban → Highway / RandomForest | 0.8469 | 0.8249 | 0.8726 | 0.0781 | 0.8916 | -0.0448 |
| Urban → Highway / XGBoost | 0.8324 | 0.8217 | 0.8755 | 0.0431 | 0.8918 | -0.0594 |
| Urban → Highway / GRU | 0.8044 | 0.8483 | 0.8828 | 0.0593 | 0.9150 | -0.1105 |
| Urban → Highway / GAT | 0.7300 | 0.7971 | 0.8315 | 0.0672 | 0.8792 | -0.1493 |
| Urban → Highway / RAVEN-X | 0.7622 | 0.8394 | 0.8695 | 0.0655 | 0.9142 | -0.1520 |
| Urban → Highway / RAVEN-X-GF | 0.7938 | 0.8561 | 0.8914 | 0.0792 | 0.9211 | -0.1273 |
| Low → High density / RandomForest | 0.8253 | 0.8067 | 0.8111 | 0.2904 | 0.8602 | -0.0348 |
| Low → High density / XGBoost | 0.7655 | 0.8411 | 0.8252 | 0.1476 | 0.8591 | -0.0935 |
| Low → High density / GRU | 0.4350 | 0.9319 | 0.8017 | 0.5058 | 0.8825 | -0.4475 |
| Low → High density / GAT | 0.6631 | 0.8258 | 0.7908 | 0.1307 | 0.8466 | -0.1835 |
| Low → High density / RAVEN-X | 0.6047 | 0.8688 | 0.7944 | 0.2297 | 0.8631 | -0.2585 |
| Low → High density / RAVEN-X-GF | 0.6974 | 0.8757 | 0.8387 | 0.1501 | 0.8863 | -0.1889 |
| highway_2 → urban_2 / XGBoost | 0.8746 | 0.8140 | 0.8934 | 0.0352 | 0.8591 | 0.0155 |
| highway_2 → urban_2 / RAVEN-X | 0.8740 | 0.8620 | 0.9265 | 0.0398 | 0.8631 | 0.0108 |
| highway_2 → urban_2 / RAVEN-X-GF | 0.8975 | 0.8630 | 0.9315 | 0.0212 | 0.8863 | 0.0112 |
| highway_7 → highway_2 / XGBoost | 0.7222 | 0.8172 | 0.8532 | 0.1162 | 0.8685 | -0.1463 |
| highway_7 → highway_2 / RAVEN-X | 0.8012 | 0.8188 | 0.8785 | 0.0731 | 0.8705 | -0.0694 |
| highway_7 → highway_2 / RAVEN-X-GF | 0.8299 | 0.8389 | 0.9015 | 0.0663 | 0.8765 | -0.0465 |
| highway_7 → urban_2 / XGBoost | 0.7767 | 0.8395 | 0.8875 | 0.0923 | 0.8685 | -0.0918 |
| highway_7 → urban_2 / RAVEN-X | 0.8566 | 0.8597 | 0.9204 | 0.0533 | 0.8705 | -0.0139 |
| highway_7 → urban_2 / RAVEN-X-GF | 0.8749 | 0.8756 | 0.9293 | 0.0543 | 0.8765 | -0.0015 |
| urban_2 → highway_2 / XGBoost | 0.8572 | 0.7818 | 0.8759 | 0.0214 | 0.8918 | -0.0347 |
| urban_2 → highway_2 / RAVEN-X | 0.8696 | 0.8335 | 0.9091 | 0.0187 | 0.9142 | -0.0446 |
| urban_2 → highway_2 / RAVEN-X-GF | 0.8644 | 0.8260 | 0.9071 | 0.0340 | 0.9211 | -0.0567 |
| urban_2 → highway_7 / XGBoost | 0.8200 | 0.8444 | 0.8761 | 0.0544 | 0.8918 | -0.0718 |
| urban_2 → highway_7 / RAVEN-X | 0.7129 | 0.8428 | 0.8512 | 0.0892 | 0.9142 | -0.2013 |
| urban_2 → highway_7 / RAVEN-X-GF | 0.7605 | 0.8731 | 0.8915 | 0.1022 | 0.9211 | -0.1606 |

## Reading the results (19 features, seed 0 only)

Interim result. Seeds 1 and 2 are running, and the 3-seed report will go to
reports/cross_scenario_19f.

- **RAVEN-X-GF has the best PR-AUC in 6 of the 7 distinct tests.** The
  exception is urban_2 → highway_2, where RAVEN-X is ahead by 0.002.
- **Training on highway_2 and testing on urban_2 transfers with no loss:**
  ΔF1 is positive for all three models.
- **Moving into the dense highway_7 scenario is still the weak spot,** and the
  new features make it worse. Low → High density PR-AUC drops for every
  neural model compared with the 17-feature run (RAVEN-X-GF 0.888 → 0.839;
  GRU F1 collapses to 0.435, ECE 0.51). The neighbour features depend on
  traffic density (neighbour count, nearest distance), so a model trained
  on sparse highway_2 sees out-of-range values on dense highway_7. The
  G5 check had already flagged them as the features that drift most
  between runs.
- **Transfers that don't involve dense traffic mostly improve or hold.**
  Urban → Highway F1 goes up for every model except RAVEN-X, and
  urban_2 → highway_2 goes up for XGBoost and RAVEN-X.
