# Experiment 1 — detection (nextgen data)

Seeds: [0, 1, 2]. Thresholds chosen on validation (max F1), metrics on test.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| RandomForest | 0.9333 ± 0.0009 | 0.9739 ± 0.0078 | 0.6793 ± 0.0008 | 0.8004 ± 0.0021 | 0.8674 ± 0.0009 | 0.8188 ± 0.0004 |
| XGBoost | 0.9334 ± 0.0003 | 0.9760 ± 0.0062 | 0.6782 ± 0.0030 | 0.8003 ± 0.0003 | 0.8697 ± 0.0021 | 0.8208 ± 0.0015 |
| GRU | 0.9571 ± 0.0012 | 0.9917 ± 0.0048 | 0.7884 ± 0.0024 | 0.8784 ± 0.0032 | 0.9115 ± 0.0021 | 0.8827 ± 0.0008 |
| GAT | 0.9268 ± 0.0005 | 0.9537 ± 0.0019 | 0.6600 ± 0.0015 | 0.7802 ± 0.0016 | 0.8441 ± 0.0029 | 0.7962 ± 0.0012 |
| RAVEN-X | 0.9541 ± 0.0016 | 0.9813 ± 0.0110 | 0.7817 ± 0.0105 | 0.8701 ± 0.0049 | 0.9103 ± 0.0034 | 0.8803 ± 0.0040 |

## Calibration (lower is better)

| Model | ECE | Brier |
|---|---|---|
| RandomForest | 0.0317 ± 0.0005 | 0.0623 ± 0.0001 |
| XGBoost | 0.0267 ± 0.0005 | 0.0612 ± 0.0004 |
| GRU | 0.0338 ± 0.0007 | 0.0411 ± 0.0008 |
| GAT | 0.0234 ± 0.0066 | 0.0655 ± 0.0009 |
| RAVEN-X | 0.0188 ± 0.0050 | 0.0433 ± 0.0015 |

## Research questions (test split)

- Q2 temporal information: GRU vs RandomForest: ΔF1 = +0.0781, ΔPR-AUC = +0.0640
- Q3 neighbour information: GAT vs RandomForest: ΔF1 = -0.0202, ΔPR-AUC = -0.0226
- Q4 spatial + temporal: RAVEN-X vs GRU: ΔF1 = -0.0083, ΔPR-AUC = -0.0024
- Q4 spatial + temporal: RAVEN-X vs GAT: ΔF1 = +0.0900, ΔPR-AUC = +0.0841

Positive deltas mean the added information helped on this data. With several --seeds, check that the gap is larger than the std before claiming it.

## Attack-wise (RAVEN-X, test)

| Attack | Precision | Recall | F1 |
|---|---|---|---|
| Constant Position Offset | 0.9813 | 0.7817 | 0.8701 |

## Attack-wise F1, all models

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X |
|---|---|---|---|---|---|
| Constant Position Offset | 0.8004 | 0.8003 | 0.8784 | 0.7802 | 0.8701 |

## Risk decision policy (RAVEN-X)

Fitted on validation: t_low = 0.043, t_high = 0.043, u_max = 0.0876 (reject precision ≥ 0.98, attack share among TRUST ≤ 0.02).

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 32541 | 0.7352 | 0.0442 | 0.1652 | 0.8749 |
| VERIFY | 5489 | 0.1240 | 0.2177 | 0.1372 | 0.1208 |
| REJECT | 6229 | 0.1407 | 0.9754 | 0.6976 | 0.0043 |

Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 37111 | 0.8385 | 0.0490 | 0.2086 | 0.9928 |
| VERIFY | 89 | 0.0020 | 0.3146 | 0.0032 | 0.0017 |
| REJECT | 7059 | 0.1595 | 0.9725 | 0.7882 | 0.0055 |

## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)

| quintile | mean_uncertainty | error_rate | n |
|---|---|---|---|
| Q1 | 0.0550 | 0.0367 | 8852 |
| Q2 | 0.0555 | 0.0407 | 8852 |
| Q3 | 0.0577 | 0.0484 | 8851 |
| Q4 | 0.0708 | 0.0241 | 8852 |
| Q5 | 0.1069 | 0.0819 | 8852 |
