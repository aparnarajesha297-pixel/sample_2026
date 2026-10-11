# Experiment 1 — detection (synthetic data)
> Synthetic data: these numbers only show the pipeline works. Do not report them as results.


Seeds: [0]. Thresholds chosen on validation (max F1), metrics on test.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| RandomForest | 0.9416 | 0.9503 | 0.6929 | 0.8015 | 0.8584 | 0.8030 |
| XGBoost | 0.9416 | 0.9520 | 0.6915 | 0.8011 | 0.8617 | 0.8049 |
| GRU | 0.9476 | 0.9662 | 0.7172 | 0.8233 | 0.8640 | 0.8150 |
| GAT | 0.9406 | 0.9353 | 0.6996 | 0.8005 | 0.8933 | 0.8233 |
| RAVEN-X | 0.9448 | 0.9360 | 0.7253 | 0.8173 | 0.9054 | 0.8371 |

## Calibration (lower is better)

| Model | ECE | Brier |
|---|---|---|
| RandomForest | 0.0293 | 0.0542 |
| XGBoost | 0.0152 | 0.0528 |
| GRU | 0.0187 | 0.0489 |
| GAT | 0.0127 | 0.0523 |
| RAVEN-X | 0.0078 | 0.0495 |

## Research questions (test split)

- Q2 temporal information: GRU vs RandomForest: ΔF1 = +0.0218, ΔPR-AUC = +0.0120
- Q3 neighbour information: GAT vs RandomForest: ΔF1 = -0.0010, ΔPR-AUC = +0.0203
- Q4 spatial + temporal: RAVEN-X vs GRU: ΔF1 = -0.0061, ΔPR-AUC = +0.0221
- Q4 spatial + temporal: RAVEN-X vs GAT: ΔF1 = +0.0168, ΔPR-AUC = +0.0138

Positive deltas mean the added information helped on this data. With several --seeds, check that the gap is larger than the std before claiming it.

## Attack-wise (RAVEN-X, test)

| Attack | Precision | Recall | F1 |
|---|---|---|---|
| Acceleration Multiplication | 0.8166 | 0.7317 | 0.7718 |
| Constant Position Offset | 0.2407 | 0.0063 | 0.0123 |
| Constant Speed Offset | 0.9933 | 0.9156 | 0.9529 |
| Data Replay | 0.9579 | 0.1601 | 0.2743 |
| DoS | 0.9987 | 0.9957 | 0.9972 |
| Feigned Braking | 0.9102 | 0.9449 | 0.9272 |
| Position Mirroring | 0.0968 | 0.0012 | 0.0024 |
| Random Position Offset | 0.9974 | 0.9592 | 0.9779 |
| Random Speed Offset | 0.8442 | 0.9357 | 0.8876 |
| Reversed Heading | 0.3829 | 0.1834 | 0.2480 |
| Sudden Constant Speed | 0.8813 | 0.7752 | 0.8249 |
| Sudden Stop | 0.9897 | 0.9936 | 0.9916 |
| Time Delay | 0.9966 | 0.9996 | 0.9981 |
| Traffic Congestion Sybil | 0.9930 | 0.9987 | 0.9959 |
| Zero Speed Report | 0.9925 | 1.0000 | 0.9962 |

## Attack-wise F1, all models

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X |
|---|---|---|---|---|---|
| Acceleration Multiplication | 0.8534 | 0.8441 | 0.8290 | 0.8059 | 0.7718 |
| Constant Position Offset | 0.0218 | 0.0104 | 0.0019 | 0.0076 | 0.0123 |
| Constant Speed Offset | 0.8996 | 0.9115 | 0.9645 | 0.8950 | 0.9529 |
| Data Replay | 0.0700 | 0.0694 | 0.2964 | 0.0610 | 0.2743 |
| DoS | 0.9914 | 0.9863 | 0.9933 | 0.9937 | 0.9972 |
| Feigned Braking | 0.9350 | 0.9239 | 0.9706 | 0.9280 | 0.9272 |
| Position Mirroring | 0.0185 | 0.0139 | 0.0016 | 0.0162 | 0.0024 |
| Random Position Offset | 0.9459 | 0.9461 | 0.9754 | 0.9464 | 0.9779 |
| Random Speed Offset | 0.8736 | 0.8710 | 0.8921 | 0.8667 | 0.8876 |
| Reversed Heading | 0.0078 | 0.0063 | 0.0028 | 0.2371 | 0.2480 |
| Sudden Constant Speed | 0.7308 | 0.7252 | 0.8377 | 0.7076 | 0.8249 |
| Sudden Stop | 0.9787 | 0.9813 | 0.9926 | 0.9868 | 0.9916 |
| Time Delay | 0.9924 | 0.9945 | 0.9943 | 0.9970 | 0.9981 |
| Traffic Congestion Sybil | 0.9921 | 0.9918 | 0.9975 | 0.9959 | 0.9959 |
| Zero Speed Report | 0.9903 | 0.9925 | 0.9975 | 0.9955 | 0.9962 |

## Risk decision policy (RAVEN-X)

Fitted on validation: t_low = 0.044, t_high = 0.098, u_max = 0.1969 (reject precision ≥ 0.98, attack share among TRUST ≤ 0.02).

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 81840 | 0.3862 | 0.0265 | 0.0600 | 0.4531 |
| VERIFY | 104548 | 0.4933 | 0.0890 | 0.2579 | 0.5416 |
| REJECT | 25537 | 0.1205 | 0.9632 | 0.6820 | 0.0053 |

Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 183919 | 0.8678 | 0.0538 | 0.2744 | 0.9896 |
| VERIFY | 1845 | 0.0087 | 0.5057 | 0.0259 | 0.0052 |
| REJECT | 26161 | 0.1234 | 0.9647 | 0.6997 | 0.0053 |

## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)

| quintile | mean_uncertainty | error_rate | n |
|---|---|---|---|
| Q1 | 0.0379 | 0.0001 | 42385 |
| Q2 | 0.0577 | 0.0289 | 42385 |
| Q3 | 0.0915 | 0.0607 | 42385 |
| Q4 | 0.1395 | 0.0768 | 42385 |
| Q5 | 0.2357 | 0.1095 | 42385 |
