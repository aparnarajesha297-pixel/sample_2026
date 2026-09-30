# Experiment 1 — detection (nextgen data)

Seeds: [0]. Thresholds chosen on validation (max F1), metrics on test.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| RandomForest | 0.8957 | 0.9959 | 0.4570 | 0.6265 | 0.7381 | 0.6370 |
| XGBoost | 0.8959 | 0.9988 | 0.4566 | 0.6267 | 0.7454 | 0.6392 |
| GRU | 0.8959 | 0.9972 | 0.4573 | 0.6271 | 0.7442 | 0.6447 |
| GAT | 0.8956 | 0.9997 | 0.4548 | 0.6252 | 0.7526 | 0.6470 |
| RAVEN-X | 0.8947 | 0.9961 | 0.4520 | 0.6219 | 0.7664 | 0.6555 |

## Calibration (lower is better)

| Model | ECE | Brier |
|---|---|---|
| RandomForest | 0.0555 | 0.1007 |
| XGBoost | 0.0323 | 0.0960 |
| GRU | 0.0133 | 0.0927 |
| GAT | 0.0279 | 0.0938 |
| RAVEN-X | 0.0148 | 0.0938 |

## Research questions (test split)

- Q2 temporal information: GRU vs XGBoost: ΔF1 = +0.0004, ΔPR-AUC = +0.0055
- Q3 neighbour information: GAT vs XGBoost: ΔF1 = -0.0015, ΔPR-AUC = +0.0078
- Q4 spatial + temporal: RAVEN-X vs GRU: ΔF1 = -0.0052, ΔPR-AUC = +0.0108
- Q4 spatial + temporal: RAVEN-X vs GAT: ΔF1 = -0.0033, ΔPR-AUC = +0.0085

Positive deltas mean the added information helped on this data. With several --seeds, check that the gap is larger than the std before claiming it.

## Attack-wise (RAVEN-X, test)

| Attack | Precision | Recall | F1 |
|---|---|---|---|
| Reversed Heading | 0.9988 | 0.9265 | 0.9613 |
| Time Delay | 0.0455 | 0.0001 | 0.0002 |

## Attack-wise F1, all models

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X |
|---|---|---|---|---|---|
| Reversed Heading | 0.9661 | 0.9660 | 0.9671 | 0.9649 | 0.9613 |
| Time Delay | 0.0011 | 0.0016 | 0.0002 | 0.0000 | 0.0002 |

## Risk decision policy (RAVEN-X)

Fitted on validation: t_low = 0.093, t_high = 0.357, u_max = 0.2216 (reject precision ≥ 0.98, attack share among TRUST ≤ 0.02).

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 2328 | 0.0263 | 0.0099 | 0.0014 | 0.0322 |
| VERIFY | 78634 | 0.8883 | 0.1195 | 0.5546 | 0.9674 |
| REJECT | 7556 | 0.0854 | 0.9959 | 0.4440 | 0.0004 |

Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 79395 | 0.8969 | 0.1139 | 0.5335 | 0.9830 |
| VERIFY | 1456 | 0.0164 | 0.1799 | 0.0155 | 0.0167 |
| REJECT | 7667 | 0.0866 | 0.9970 | 0.4510 | 0.0003 |

## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)

| quintile | mean_uncertainty | error_rate | n |
|---|---|---|---|
| Q1 | 0.1453 | 0.0468 | 17704 |
| Q2 | 0.1777 | 0.0994 | 17703 |
| Q3 | 0.1851 | 0.1136 | 17704 |
| Q4 | 0.1994 | 0.1163 | 17703 |
| Q5 | 0.2458 | 0.1502 | 17704 |
