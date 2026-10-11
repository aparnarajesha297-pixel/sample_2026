# Threshold sweep (row 14)

Beliefs: temperature-scaled P(attack) from `results/svoi_hw2/beliefs.npz` (T = 0.778, fitted on validation). Threshold chosen on validation only: **0.8**.

| Threshold | test Precision | test Recall | test F1 | test FPR | test FNR | val F1 |
|---|---|---|---|---|---|---|
| 0.1000 | 0.5969 | 0.9039 | 0.7190 | 0.1502 | 0.0961 | 0.7981 |
| 0.2000 | 0.7786 | 0.8742 | 0.8236 | 0.0612 | 0.1258 | 0.8839 |
| 0.3000 | 0.8373 | 0.8644 | 0.8506 | 0.0413 | 0.1356 | 0.8996 |
| 0.4000 | 0.8705 | 0.8582 | 0.8643 | 0.0314 | 0.1418 | 0.9048 |
| 0.5000 | 0.8987 | 0.8508 | 0.8741 | 0.0236 | 0.1492 | 0.9095 |
| 0.6000 | 0.9079 | 0.8470 | 0.8764 | 0.0211 | 0.1530 | 0.9099 |
| 0.7000 | 0.9138 | 0.8447 | 0.8779 | 0.0196 | 0.1553 | 0.9103 |
| 0.8000 | 0.9208 | 0.8415 | 0.8793 | 0.0178 | 0.1585 | 0.9108 |
| 0.9000 | 0.9356 | 0.8336 | 0.8816 | 0.0141 | 0.1664 | 0.9098 |

## Chosen threshold vs other rules (test)

| Rule | Threshold | Precision | Recall | F1 | FPR | FNR |
|---|---|---|---|---|---|---|
| grid choice (max validation F1) | 0.8000 | 0.9208 | 0.8415 | 0.8793 | 0.0178 | 0.1585 |
| continuous max-validation-F1 threshold | 0.7946 | 0.9203 | 0.8417 | 0.8792 | 0.0179 | 0.1583 |
| cost-based SVoI boundary C_FR/(C_FA+C_FR) | 0.1667 | 0.7422 | 0.8805 | 0.8054 | 0.0753 | 0.1195 |
