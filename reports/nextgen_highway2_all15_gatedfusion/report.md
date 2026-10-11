# Experiment 1 — detection (nextgen data)

Seeds: [0, 1, 2]. Thresholds chosen on validation (max F1), metrics on test.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|
| RandomForest | 0.9248 ± 0.0032 | 0.8338 ± 0.0213 | 0.7744 ± 0.0099 | 0.8028 ± 0.0047 | 0.9054 ± 0.0003 | 0.8489 ± 0.0004 |
| XGBoost | 0.9232 ± 0.0018 | 0.8303 ± 0.0097 | 0.7680 ± 0.0024 | 0.7979 ± 0.0032 | 0.9066 ± 0.0003 | 0.8556 ± 0.0010 |
| GRU | 0.9345 ± 0.0009 | 0.8445 ± 0.0141 | 0.8197 ± 0.0153 | 0.8317 ± 0.0018 | 0.9393 ± 0.0020 | 0.8935 ± 0.0045 |
| GAT | 0.9434 ± 0.0007 | 0.9351 ± 0.0068 | 0.7666 ± 0.0038 | 0.8425 ± 0.0014 | 0.9158 ± 0.0015 | 0.8763 ± 0.0014 |
| RAVEN-X | 0.9500 ± 0.0033 | 0.9167 ± 0.0187 | 0.8217 ± 0.0021 | 0.8665 ± 0.0075 | 0.9448 ± 0.0018 | 0.9132 ± 0.0036 |
| RAVEN-X-GF | 0.9520 ± 0.0026 | 0.9105 ± 0.0125 | 0.8394 ± 0.0058 | 0.8735 ± 0.0063 | 0.9445 ± 0.0010 | 0.9174 ± 0.0022 |

## Calibration (lower is better)

| Model | ECE | Brier |
|---|---|---|
| RandomForest | 0.1375 ± 0.0005 | 0.0942 ± 0.0005 |
| XGBoost | 0.0321 ± 0.0007 | 0.0648 ± 0.0007 |
| GRU | 0.0211 ± 0.0101 | 0.0535 ± 0.0026 |
| GAT | 0.0190 ± 0.0021 | 0.0510 ± 0.0004 |
| RAVEN-X | 0.0340 ± 0.0116 | 0.0516 ± 0.0064 |
| RAVEN-X-GF | 0.0376 ± 0.0147 | 0.0468 ± 0.0065 |

## Research questions (test split)

- Q2 temporal information: GRU vs RandomForest: ΔF1 = +0.0289, ΔPR-AUC = +0.0446
- Q3 neighbour information: GAT vs RandomForest: ΔF1 = +0.0397, ΔPR-AUC = +0.0274
- Q4 spatial + temporal: RAVEN-X vs GRU: ΔF1 = +0.0348, ΔPR-AUC = +0.0197
- Q4 spatial + temporal: RAVEN-X vs GAT: ΔF1 = +0.0240, ΔPR-AUC = +0.0369
- Gated fusion: RAVEN-X-GF vs RAVEN-X: ΔF1 = +0.0070, ΔPR-AUC = +0.0041
- Gated fusion: RAVEN-X-GF vs GRU: ΔF1 = +0.0418, ΔPR-AUC = +0.0238
- Gated fusion: RAVEN-X-GF vs GAT: ΔF1 = +0.0310, ΔPR-AUC = +0.0410

Positive deltas mean the added information helped on this data. With several --seeds, check that the gap is larger than the std before claiming it.

## Attack-wise (RAVEN-X, test)

| Attack | Precision | Recall | F1 |
|---|---|---|---|
| Acceleration Multiplication | 0.7381 | 0.5712 | 0.6430 |
| Constant Position Offset | 0.9042 | 0.7579 | 0.8243 |
| Constant Speed Offset | 0.9458 | 0.9124 | 0.9288 |
| Data Replay | 0.8857 | 0.7185 | 0.7932 |
| DoS | 0.9394 | 1.0000 | 0.9687 |
| Feigned Braking | 0.8040 | 0.8762 | 0.8382 |
| Position Mirroring | 0.8689 | 0.4405 | 0.5842 |
| Random Position Offset | 0.9306 | 0.9763 | 0.9528 |
| Random Speed Offset | 0.9321 | 0.9291 | 0.9306 |
| Reversed Heading | 0.9252 | 0.9370 | 0.9310 |
| Sudden Constant Speed | 0.5979 | 0.9030 | 0.7177 |
| Sudden Stop | 0.7688 | 0.7084 | 0.7332 |
| Time Delay | 0.1528 | 0.0149 | 0.0270 |
| Traffic Congestion Sybil | 0.9798 | 0.9926 | 0.9862 |
| Zero Speed Report | 0.9340 | 0.9537 | 0.9436 |

## Attack-wise F1, all models

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X | RAVEN-X-GF |
|---|---|---|---|---|---|---|
| Acceleration Multiplication | 0.7428 | 0.7793 | 0.7302 | 0.8194 | 0.6430 | 0.7768 |
| Constant Position Offset | 0.7458 | 0.7450 | 0.8188 | 0.7569 | 0.8243 | 0.8314 |
| Constant Speed Offset | 0.8810 | 0.8872 | 0.9097 | 0.9163 | 0.9288 | 0.9294 |
| Data Replay | 0.3627 | 0.3512 | 0.7831 | 0.2748 | 0.7932 | 0.7822 |
| DoS | 0.9229 | 0.9226 | 0.9284 | 0.9817 | 0.9687 | 0.9631 |
| Feigned Braking | 0.7418 | 0.8000 | 0.7893 | 0.8871 | 0.8382 | 0.8391 |
| Position Mirroring | 0.3139 | 0.3200 | 0.6063 | 0.2759 | 0.5842 | 0.6294 |
| Random Position Offset | 0.9213 | 0.9212 | 0.9269 | 0.9660 | 0.9528 | 0.9503 |
| Random Speed Offset | 0.9072 | 0.9035 | 0.9121 | 0.9363 | 0.9306 | 0.9291 |
| Reversed Heading | 0.9115 | 0.9081 | 0.9103 | 0.9442 | 0.9310 | 0.9267 |
| Sudden Constant Speed | 0.5646 | 0.5909 | 0.6001 | 0.7201 | 0.7177 | 0.7077 |
| Sudden Stop | 0.8101 | 0.8139 | 0.7688 | 0.6931 | 0.7332 | 0.8210 |
| Time Delay | 0.0597 | 0.0576 | 0.0509 | 0.0137 | 0.0270 | 0.0192 |
| Traffic Congestion Sybil | 0.9413 | 0.9181 | 0.9145 | 0.9937 | 0.9862 | 0.9886 |
| Zero Speed Report | 0.9224 | 0.9199 | 0.9163 | 0.9592 | 0.9436 | 0.9432 |

## Gated fusion: what each attack relies on (RAVEN-X-GF, test)

Mean gate g: 1 = the prediction came from the GRU (time) branch, 0 = from the GAT (neighbour) branch.

| Attack | gate on benign | gate on attacks |
|---|---|---|
| Acceleration Multiplication | 0.7100 | 0.7030 |
| Constant Position Offset | 0.7050 | 0.7320 |
| Constant Speed Offset | 0.7080 | 0.7750 |
| Data Replay | 0.7070 | 0.7620 |
| DoS | 0.6990 | 0.5650 |
| Feigned Braking | 0.7050 | 0.6020 |
| Position Mirroring | 0.7100 | 0.7810 |
| Random Position Offset | 0.7030 | 0.7140 |
| Random Speed Offset | 0.7080 | 0.7530 |
| Reversed Heading | 0.7080 | 0.6870 |
| Sudden Constant Speed | 0.7090 | 0.7200 |
| Sudden Stop | 0.7090 | 0.7500 |
| Time Delay | 0.7090 | 0.7060 |
| Traffic Congestion Sybil | 0.7060 | 0.3860 |
| Zero Speed Report | 0.7060 | 0.7210 |

## Risk decision policy (RAVEN-X)

Fitted on validation: t_low = 0.047, t_high = 0.766, u_max = 0.1535 (reject precision ≥ 0.98, attack share among TRUST ≤ 0.02).

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 399453 | 0.5678 | 0.0245 | 0.0705 | 0.6902 |
| VERIFY | 186528 | 0.2651 | 0.0955 | 0.1282 | 0.2988 |
| REJECT | 117539 | 0.1671 | 0.9473 | 0.8014 | 0.0110 |

Fixed initial levels (TRUST < 0.30, REJECT ≥ 0.80, no uncertainty):

| decision | count | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|---|
| TRUST | 557006 | 0.7917 | 0.0365 | 0.1462 | 0.9506 |
| VERIFY | 19603 | 0.0279 | 0.2035 | 0.0287 | 0.0277 |
| REJECT | 126911 | 0.1804 | 0.9033 | 0.8250 | 0.0217 |

## Uncertainty vs error (RAVEN-X, test, quintiles of uncertainty)

| quintile | mean_uncertainty | error_rate | n |
|---|---|---|---|
| Q1 | 0.0271 | 0.0089 | 140704 |
| Q2 | 0.0409 | 0.0242 | 140704 |
| Q3 | 0.0571 | 0.0331 | 140704 |
| Q4 | 0.0901 | 0.0517 | 140704 |
| Q5 | 0.2853 | 0.1359 | 140704 |
