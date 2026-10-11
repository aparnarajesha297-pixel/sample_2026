# Cross-scenario generalisation, 3 seeds (row 6)

Seeds [0, 1, 2]. Train on the source domain's train/val split (threshold picked on source validation), test on the target domain's test split. In-domain F1 is the same model on the source test split. Values are mean ± std over seeds.

`highway_2 → highway_7` is the same experiment as `Low → High density` (one scenario per density) and is copied from it.

## Urban → Highway

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| RandomForest | 0.8129 ± 0.0017 | 0.8204 ± 0.0023 | 0.8576 ± 0.0004 | 0.0674 ± 0.0006 | 0.8655 ± 0.0004 | -0.0526 ± 0.0013 | 3 |
| XGBoost | 0.8080 ± 0.0032 | 0.8168 ± 0.0045 | 0.8591 ± 0.0002 | 0.0350 ± 0.0016 | 0.8657 ± 0.0001 | -0.0577 ± 0.0032 | 3 |
| GRU | 0.8104 ± 0.0132 | 0.8455 ± 0.0066 | 0.8716 ± 0.0084 | 0.0413 ± 0.0027 | 0.8918 ± 0.0043 | -0.0814 ± 0.0089 | 3 |
| GAT | 0.7098 ± 0.0433 | 0.8161 ± 0.0137 | 0.8581 ± 0.0053 | 0.0827 ± 0.0347 | 0.8806 ± 0.0016 | -0.1708 ± 0.0442 | 3 |
| RAVEN-X | 0.7646 ± 0.0353 | 0.8454 ± 0.0104 | 0.8863 ± 0.0095 | 0.0679 ± 0.0107 | 0.9082 ± 0.0028 | -0.1436 ± 0.0352 | 3 |
| RAVEN-X-GF | 0.7840 ± 0.0100 | 0.8606 ± 0.0076 | 0.8917 ± 0.0078 | 0.0784 ± 0.0039 | 0.9184 ± 0.0013 | -0.1344 ± 0.0092 | 3 |

## Low → High density

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| RandomForest | 0.8036 ± 0.0079 | 0.7572 ± 0.0197 | 0.8583 ± 0.0008 | 0.1841 ± 0.0015 | 0.8028 ± 0.0037 | 0.0008 ± 0.0117 | 3 |
| XGBoost | 0.8196 ± 0.0077 | 0.7960 ± 0.0094 | 0.8645 ± 0.0038 | 0.0405 ± 0.0031 | 0.7962 ± 0.0032 | 0.0233 ± 0.0046 | 3 |
| GRU | 0.7404 ± 0.0443 | 0.8123 ± 0.0307 | 0.8164 ± 0.0384 | 0.0675 ± 0.0280 | 0.8297 ± 0.0049 | -0.0893 ± 0.0408 | 3 |
| GAT | 0.5713 ± 0.0404 | 0.8687 ± 0.0122 | 0.8319 ± 0.0270 | 0.2422 ± 0.0520 | 0.8426 ± 0.0020 | -0.2714 ± 0.0395 | 3 |
| RAVEN-X | 0.6506 ± 0.0505 | 0.8740 ± 0.0266 | 0.8116 ± 0.0538 | 0.1923 ± 0.0597 | 0.8679 ± 0.0015 | -0.2173 ± 0.0520 | 3 |
| RAVEN-X-GF | 0.6805 ± 0.0369 | 0.8856 ± 0.0143 | 0.8657 ± 0.0281 | 0.1745 ± 0.0337 | 0.8798 ± 0.0081 | -0.1993 ± 0.0318 | 3 |

## highway_2 → urban_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8530 ± 0.0009 | 0.7923 ± 0.0070 | 0.8854 ± 0.0006 | 0.0150 ± 0.0012 | 0.7962 ± 0.0032 | 0.0568 ± 0.0037 | 3 |
| RAVEN-X | 0.8882 ± 0.0023 | 0.8634 ± 0.0079 | 0.9323 ± 0.0021 | 0.0273 ± 0.0066 | 0.8682 ± 0.0020 | 0.0200 ± 0.0017 | 3 |
| RAVEN-X-GF | 0.9026 ± 0.0033 | 0.8763 ± 0.0007 | 0.9374 ± 0.0011 | 0.0282 ± 0.0117 | 0.8754 ± 0.0026 | 0.0272 ± 0.0027 | 3 |

## highway_7 → highway_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8075 ± 0.0019 | 0.7775 ± 0.0044 | 0.8575 ± 0.0004 | 0.0077 ± 0.0005 | 0.8526 ± 0.0042 | -0.0451 ± 0.0023 | 3 |
| RAVEN-X | 0.8510 ± 0.0054 | 0.8305 ± 0.0083 | 0.9034 ± 0.0017 | 0.0442 ± 0.0148 | 0.8331 ± 0.0070 | 0.0179 ± 0.0124 | 3 |
| RAVEN-X-GF | 0.8636 ± 0.0082 | 0.8488 ± 0.0047 | 0.9113 ± 0.0014 | 0.0720 ± 0.0092 | 0.8722 ± 0.0059 | -0.0086 ± 0.0093 | 3 |

## highway_7 → urban_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8618 ± 0.0021 | 0.8164 ± 0.0039 | 0.8875 ± 0.0006 | 0.0171 ± 0.0001 | 0.8526 ± 0.0042 | 0.0091 ± 0.0021 | 3 |
| RAVEN-X | 0.8889 ± 0.0054 | 0.8667 ± 0.0007 | 0.9309 ± 0.0023 | 0.0307 ± 0.0119 | 0.8316 ± 0.0087 | 0.0573 ± 0.0082 | 3 |
| RAVEN-X-GF | 0.8988 ± 0.0025 | 0.8811 ± 0.0026 | 0.9360 ± 0.0007 | 0.0568 ± 0.0091 | 0.8574 ± 0.0221 | 0.0414 ± 0.0221 | 3 |

## urban_2 → highway_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.7761 ± 0.0024 | 0.7792 ± 0.0055 | 0.8393 ± 0.0013 | 0.0400 ± 0.0006 | 0.8657 ± 0.0001 | -0.0896 ± 0.0024 | 3 |
| RAVEN-X | 0.8543 ± 0.0126 | 0.8249 ± 0.0089 | 0.8987 ± 0.0105 | 0.0224 ± 0.0108 | 0.9103 ± 0.0020 | -0.0560 ± 0.0108 | 3 |
| RAVEN-X-GF | 0.8656 ± 0.0160 | 0.8380 ± 0.0078 | 0.9102 ± 0.0051 | 0.0249 ± 0.0096 | 0.9152 ± 0.0022 | -0.0496 ± 0.0147 | 3 |

## urban_2 → highway_7

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8259 ± 0.0056 | 0.8381 ± 0.0040 | 0.8699 ± 0.0008 | 0.0335 ± 0.0027 | 0.8657 ± 0.0001 | -0.0398 ± 0.0055 | 3 |
| RAVEN-X | 0.7363 ± 0.0613 | 0.8763 ± 0.0190 | 0.8925 ± 0.0136 | 0.1058 ± 0.0500 | 0.9146 ± 0.0029 | -0.1784 ± 0.0614 | 3 |
| RAVEN-X-GF | 0.7304 ± 0.0415 | 0.8740 ± 0.0146 | 0.8880 ± 0.0220 | 0.1081 ± 0.0127 | 0.9184 ± 0.0008 | -0.1880 ± 0.0407 | 3 |

## highway_2 → highway_7

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8196 ± 0.0077 | 0.7960 ± 0.0094 | 0.8645 ± 0.0038 | 0.0405 ± 0.0031 | 0.7962 ± 0.0032 | 0.0233 ± 0.0046 | 3 |
| RAVEN-X | 0.6506 ± 0.0505 | 0.8740 ± 0.0266 | 0.8116 ± 0.0538 | 0.1923 ± 0.0597 | 0.8679 ± 0.0015 | -0.2173 ± 0.0520 | 3 |
| RAVEN-X-GF | 0.6805 ± 0.0369 | 0.8856 ± 0.0143 | 0.8657 ± 0.0281 | 0.1745 ± 0.0337 | 0.8798 ± 0.0081 | -0.1993 ± 0.0318 | 3 |

## PR-AUC summary (mean over seeds)

| Test | RandomForest | XGBoost | GRU | GAT | RAVEN-X | RAVEN-X-GF |
|---|---|---|---|---|---|---|
| Urban → Highway | 0.8576 | 0.8591 | 0.8716 | 0.8581 | 0.8863 | 0.8917 |
| Low → High density | 0.8583 | 0.8645 | 0.8164 | 0.8319 | 0.8116 | 0.8657 |
| highway_2 → urban_2 | – | 0.8854 | – | – | 0.9323 | 0.9374 |
| highway_7 → highway_2 | – | 0.8575 | – | – | 0.9034 | 0.9113 |
| highway_7 → urban_2 | – | 0.8875 | – | – | 0.9309 | 0.9360 |
| urban_2 → highway_2 | – | 0.8393 | – | – | 0.8987 | 0.9102 |
| urban_2 → highway_7 | – | 0.8699 | – | – | 0.8925 | 0.8880 |
| highway_2 → highway_7 | – | 0.8645 | – | – | 0.8116 | 0.8657 |
## Reading the table

- Of the 7 distinct tests, RAVEN-X-GF has the highest mean PR-AUC in 6. Two of those 6 are close calls. In Low → High density it beats XGBoost by only 0.001 (0.8657 vs 0.8645), which is inside the seed std. In urban_2 → highway_7, RAVEN-X is slightly ahead of GF (0.8925 vs 0.8880), also inside the std.
- Transfer into highway_7 is where the neural models struggle. Their F1 falls 0.18–0.27 below in-domain, their ECE rises to 0.10–0.24, and their PR-AUC mostly holds. The ranking still works, but the threshold and calibration picked on the source validation set no longer fit the target. XGBoost keeps its F1 here and wins on F1. Recalibrating or re-thresholding on a small labelled target sample would probably close most of this gap, but we haven't tested that.
- Transfers into urban_2 score above in-domain for every model. urban_2's test split looks easier, so a negative ΔF1 is the more telling signal.
- highway_7 has only 3% of its receivers loaded, so any test that trains on highway_7 uses a small training set.
- RAVEN-X-GF training isn't fully deterministic for a fixed seed. Seed 0 trained highway_2 → highway_7 twice before the dedup was added: F1 was 0.668 and 0.616, and PR-AUC was 0.888 and 0.868. XGBoost and RAVEN-X reproduced exactly. The std values above understate GF's real spread a little.
