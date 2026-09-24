# Experiment 1 — detection (nextgen data)

Seeds: [0, 1, 2]. Thresholds chosen on validation (max F1), metrics on test.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| RandomForest | 0.9019 ± 0.0031 | 0.7671 ± 0.0159 | 0.7232 ± 0.0058 | 0.7444 ± 0.0045 | 0.8684 ± 0.0001 | 0.8017 ± 0.0004 |
| XGBoost | 0.9119 ± 0.0017 | 0.8201 ± 0.0104 | 0.7100 ± 0.0032 | 0.7610 ± 0.0029 | 0.8700 ± 0.0006 | 0.8069 ± 0.0011 |
| GRU | 0.9078 ± 0.0067 | 0.7696 ± 0.0248 | 0.7619 ± 0.0056 | 0.7656 ± 0.0137 | 0.9016 ± 0.0047 | 0.8221 ± 0.0154 |
| GAT | 0.9340 ± 0.0022 | 0.9402 ± 0.0172 | 0.7110 ± 0.0028 | 0.8096 ± 0.0046 | 0.8829 ± 0.0010 | 0.8355 ± 0.0020 |
| RAVEN-X | 0.9343 ± 0.0079 | 0.8923 ± 0.0443 | 0.7609 ± 0.0141 | 0.8209 ± 0.0171 | 0.9124 ± 0.0009 | 0.8693 ± 0.0053 |

## Calibration (lower is better)

| Model | ECE | Brier |
|---|---|---|
| RandomForest | 0.1916 ± 0.0009 | 0.1281 ± 0.0004 |
| XGBoost | 0.0389 ± 0.0073 | 0.0760 ± 0.0021 |
| GRU | 0.0435 ± 0.0148 | 0.0771 ± 0.0070 |
| GAT | 0.0270 ± 0.0025 | 0.0618 ± 0.0013 |
| RAVEN-X | 0.0527 ± 0.0313 | 0.0714 ± 0.0165 |

## Research questions (test split)

- Q2 temporal information: GRU vs XGBoost: ΔF1 = +0.0045, ΔPR-AUC = +0.0152
- Q3 neighbour information: GAT vs XGBoost: ΔF1 = +0.0486, ΔPR-AUC = +0.0286
- Q4 spatial + temporal: RAVEN-X vs GRU: ΔF1 = +0.0553, ΔPR-AUC = +0.0472
- Q4 spatial + temporal: RAVEN-X vs GAT: ΔF1 = +0.0112, ΔPR-AUC = +0.0338

Positive deltas mean the added information helped on this data. With several --seeds, check that the gap is larger than the std before claiming it.

## Attack-wise (RAVEN-X, test)

| Attack | Precision | Recall | F1 |
|---|---|---|---|
| Acceleration Multiplication | 0.6933 | 0.5386 | 0.5998 |
| Constant Position Offset | 0.8832 | 0.7644 | 0.8190 |
| Constant Speed Offset | 0.9205 | 0.8916 | 0.9055 |
| Data Replay | 0.8756 | 0.6846 | 0.7676 |
| DoS | 0.9277 | 1.0000 | 0.9622 |
| Feigned Braking | 0.7754 | 0.8311 | 0.7999 |
| Position Mirroring | 0.8293 | 0.4405 | 0.5741 |
| Random Position Offset | 0.9162 | 0.9766 | 0.9452 |
| Random Speed Offset | 0.9114 | 0.9188 | 0.9148 |
| Reversed Heading | 0.1267 | 0.0158 | 0.0276 |
| Sudden Constant Speed | 0.5620 | 0.8519 | 0.6740 |
| Sudden Stop | 0.7220 | 0.6599 | 0.6853 |
| Time Delay | 0.1840 | 0.0218 | 0.0384 |
| Traffic Congestion Sybil | 0.9743 | 0.9976 | 0.9858 |
| Zero Speed Report | 0.9249 | 0.9522 | 0.9381 |

## Attack-wise F1, all models

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X |
|---|---|---|---|---|---|
| Acceleration Multiplication | 0.7232 | 0.7715 | 0.6944 | 0.8316 | 0.5998 |
| Constant Position Offset | 0.7208 | 0.7402 | 0.7884 | 0.7638 | 0.8190 |
| Constant Speed Offset | 0.8605 | 0.8889 | 0.8763 | 0.9108 | 0.9055 |
| Data Replay | 0.2992 | 0.2995 | 0.7420 | 0.2633 | 0.7676 |
| DoS | 0.8952 | 0.9265 | 0.8974 | 0.9833 | 0.9622 |
| Feigned Braking | 0.7071 | 0.8041 | 0.7274 | 0.8902 | 0.7999 |
| Position Mirroring | 0.3382 | 0.3346 | 0.5855 | 0.3073 | 0.5741 |
| Random Position Offset | 0.8912 | 0.9217 | 0.8920 | 0.9664 | 0.9452 |
| Random Speed Offset | 0.8812 | 0.9054 | 0.8762 | 0.9358 | 0.9148 |
| Reversed Heading | 0.0700 | 0.0573 | 0.0863 | 0.0090 | 0.0276 |
| Sudden Constant Speed | 0.5131 | 0.5916 | 0.5072 | 0.7469 | 0.6740 |
| Sudden Stop | 0.7637 | 0.8199 | 0.6912 | 0.7466 | 0.6853 |
| Time Delay | 0.0814 | 0.0623 | 0.0732 | 0.0108 | 0.0384 |
| Traffic Congestion Sybil | 0.9309 | 0.9159 | 0.8964 | 0.9933 | 0.9858 |
| Zero Speed Report | 0.8924 | 0.9222 | 0.8830 | 0.9682 | 0.9381 |

## Risk decision policy (RAVEN-X)

Fitted on validation: t_low = 0.024, t_high = 0.913, u_max = 0.1767 (reject precision ≥ 0.98, attack share among TRUST ≤ 0.02).

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 74143 | 0.1054 | 0.0263 | 0.0140 | 0.1279 |
| VERIFY | 524227 | 0.7451 | 0.0675 | 0.2547 | 0.8658 |
| REJECT | 105150 | 0.1495 | 0.9662 | 0.7312 | 0.0063 |

Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 576371 | 0.8193 | 0.0511 | 0.2120 | 0.9687 |
| VERIFY | 15464 | 0.0220 | 0.2808 | 0.0313 | 0.0197 |
| REJECT | 111685 | 0.1588 | 0.9415 | 0.7568 | 0.0116 |

## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)

| quintile | mean_uncertainty | error_rate | n |
|---|---|---|---|
| Q1 | 0.0311 | 0.0113 | 140704 |
| Q2 | 0.0579 | 0.0416 | 140704 |
| Q3 | 0.0837 | 0.0476 | 140704 |
| Q4 | 0.1213 | 0.0590 | 140704 |
| Q5 | 0.2709 | 0.1408 | 140704 |
