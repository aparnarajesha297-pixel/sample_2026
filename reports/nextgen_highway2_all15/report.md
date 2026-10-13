# Experiment 1 — detection (nextgen data)

Seeds: [0, 1, 2]. Thresholds chosen on validation (max F1), metrics on test.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| RandomForest | 0.9263 ± 0.0005 | 0.8427 ± 0.0040 | 0.7707 ± 0.0020 | 0.8051 ± 0.0007 | 0.9043 ± 0.0001 | 0.8541 ± 0.0003 |
| XGBoost | 0.9298 ± 0.0004 | 0.8693 ± 0.0109 | 0.7591 ± 0.0130 | 0.8103 ± 0.0029 | 0.9054 ± 0.0002 | 0.8580 ± 0.0002 |
| GRU | 0.9335 ± 0.0017 | 0.8371 ± 0.0067 | 0.8234 ± 0.0051 | 0.8302 ± 0.0040 | 0.9388 ± 0.0011 | 0.8911 ± 0.0032 |
| GAT | 0.9452 ± 0.0021 | 0.9425 ± 0.0114 | 0.7698 ± 0.0012 | 0.8474 ± 0.0052 | 0.9168 ± 0.0013 | 0.8786 ± 0.0024 |
| RAVEN-X | 0.9551 ± 0.0006 | 0.9369 ± 0.0037 | 0.8284 ± 0.0029 | 0.8793 ± 0.0015 | 0.9463 ± 0.0009 | 0.9184 ± 0.0005 |

## Calibration (lower is better)

| Model | ECE | Brier |
|---|---|---|
| RandomForest | 0.1108 ± 0.0004 | 0.0798 ± 0.0001 |
| XGBoost | 0.0178 ± 0.0022 | 0.0591 ± 0.0004 |
| GRU | 0.0178 ± 0.0042 | 0.0532 ± 0.0006 |
| GAT | 0.0147 ± 0.0011 | 0.0490 ± 0.0013 |
| RAVEN-X | 0.0212 ± 0.0045 | 0.0428 ± 0.0025 |

## Research questions (test split)

- Q2 temporal information: GRU vs XGBoost: ΔF1 = +0.0199, ΔPR-AUC = +0.0331
- Q3 neighbour information: GAT vs XGBoost: ΔF1 = +0.0371, ΔPR-AUC = +0.0206
- Q4 spatial + temporal: RAVEN-X vs GRU: ΔF1 = +0.0491, ΔPR-AUC = +0.0273
- Q4 spatial + temporal: RAVEN-X vs GAT: ΔF1 = +0.0319, ΔPR-AUC = +0.0398

Positive deltas mean the added information helped on this data. With several --seeds, check that the gap is larger than the std before claiming it.

## Attack-wise (RAVEN-X, test)

| Attack | Precision | Recall | F1 |
|---|---|---|---|
| Acceleration Multiplication | 0.7973 | 0.7090 | 0.7494 |
| Constant Position Offset | 0.9266 | 0.7673 | 0.8395 |
| Constant Speed Offset | 0.9551 | 0.9073 | 0.9306 |
| Data Replay | 0.9020 | 0.7075 | 0.7929 |
| DoS | 0.9586 | 0.9999 | 0.9788 |
| Feigned Braking | 0.8488 | 0.8648 | 0.8563 |
| Position Mirroring | 0.8978 | 0.4399 | 0.5902 |
| Random Position Offset | 0.9484 | 0.9788 | 0.9634 |
| Random Speed Offset | 0.9460 | 0.9290 | 0.9375 |
| Reversed Heading | 0.9463 | 0.9368 | 0.9415 |
| Sudden Constant Speed | 0.6396 | 0.8457 | 0.7282 |
| Sudden Stop | 0.8359 | 0.7879 | 0.8110 |
| Time Delay | 0.1940 | 0.0129 | 0.0242 |
| Traffic Congestion Sybil | 0.9866 | 0.9975 | 0.9920 |
| Zero Speed Report | 0.9560 | 0.9589 | 0.9575 |

## Attack-wise F1, all models

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X |
|---|---|---|---|---|---|
| Acceleration Multiplication | 0.7412 | 0.8149 | 0.7588 | 0.8299 | 0.7494 |
| Constant Position Offset | 0.7498 | 0.7552 | 0.8140 | 0.7630 | 0.8395 |
| Constant Speed Offset | 0.8900 | 0.9077 | 0.9092 | 0.9238 | 0.9306 |
| Data Replay | 0.2882 | 0.2949 | 0.7757 | 0.2713 | 0.7929 |
| DoS | 0.9284 | 0.9430 | 0.9244 | 0.9856 | 0.9788 |
| Feigned Braking | 0.7627 | 0.8450 | 0.7818 | 0.8893 | 0.8563 |
| Position Mirroring | 0.3299 | 0.3293 | 0.6230 | 0.2871 | 0.5902 |
| Random Position Offset | 0.9286 | 0.9412 | 0.9229 | 0.9692 | 0.9634 |
| Random Speed Offset | 0.9122 | 0.9245 | 0.9084 | 0.9392 | 0.9375 |
| Reversed Heading | 0.9134 | 0.9239 | 0.9030 | 0.9483 | 0.9415 |
| Sudden Constant Speed | 0.5904 | 0.6558 | 0.6028 | 0.7222 | 0.7282 |
| Sudden Stop | 0.8268 | 0.8508 | 0.8057 | 0.7609 | 0.8110 |
| Time Delay | 0.0554 | 0.0475 | 0.0492 | 0.0119 | 0.0242 |
| Traffic Congestion Sybil | 0.9399 | 0.9138 | 0.9077 | 0.9941 | 0.9920 |
| Zero Speed Report | 0.9281 | 0.9402 | 0.9204 | 0.9665 | 0.9575 |

## Risk decision policy (RAVEN-X)

Fitted on validation: t_low = 0.051, t_high = 0.934, u_max = 0.1795 (reject precision ≥ 0.98, attack share among TRUST ≤ 0.02).

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 419966 | 0.5969 | 0.0246 | 0.0745 | 0.7255 |
| VERIFY | 166636 | 0.2369 | 0.0986 | 0.1183 | 0.2660 |
| REJECT | 116918 | 0.1662 | 0.9593 | 0.8072 | 0.0084 |

Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 563955 | 0.8016 | 0.0353 | 0.1431 | 0.9637 |
| VERIFY | 14235 | 0.0202 | 0.2094 | 0.0215 | 0.0199 |
| REJECT | 125330 | 0.1781 | 0.9262 | 0.8354 | 0.0164 |

## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)

| quintile | mean_uncertainty | error_rate | n |
|---|---|---|---|
| Q1 | 0.0228 | 0.0072 | 140704 |
| Q2 | 0.0381 | 0.0251 | 140704 |
| Q3 | 0.0564 | 0.0313 | 140704 |
| Q4 | 0.0893 | 0.0471 | 140704 |
| Q5 | 0.2640 | 0.1143 | 140704 |
