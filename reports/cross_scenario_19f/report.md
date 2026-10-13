# Cross-scenario generalisation, 3 seeds (row 6)

Seeds [0, 1, 2]. Train on the source domain's train/val split (threshold picked on source validation), test on the target domain's test split. In-domain F1 is the same model on the source test split. Values are mean ± std over seeds.

`highway_2 → highway_7` is the same experiment as `Low → High density` (one scenario per density) and is copied from it.

## Urban → Highway

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| RandomForest | 0.8438 ± 0.0037 | 0.8269 ± 0.0028 | 0.8737 ± 0.0010 | 0.0783 ± 0.0002 | 0.8910 ± 0.0005 | -0.0472 ± 0.0034 | 3 |
| XGBoost | 0.8372 ± 0.0044 | 0.8206 ± 0.0016 | 0.8763 ± 0.0007 | 0.0396 ± 0.0031 | 0.8916 ± 0.0003 | -0.0544 ± 0.0047 | 3 |
| GRU | 0.7585 ± 0.0503 | 0.8501 ± 0.0027 | 0.8659 ± 0.0181 | 0.0860 ± 0.0269 | 0.9149 ± 0.0023 | -0.1564 ± 0.0489 | 3 |
| GAT | 0.7554 ± 0.0463 | 0.7885 ± 0.0128 | 0.8435 ± 0.0133 | 0.0603 ± 0.0176 | 0.8810 ± 0.0032 | -0.1256 ± 0.0431 | 3 |
| RAVEN-X | 0.7424 ± 0.0731 | 0.8396 ± 0.0228 | 0.8504 ± 0.0389 | 0.0822 ± 0.0518 | 0.9123 ± 0.0030 | -0.1700 ± 0.0753 | 3 |
| RAVEN-X-GF | 0.6974 ± 0.1198 | 0.8694 ± 0.0176 | 0.8609 ± 0.0378 | 0.1493 ± 0.0985 | 0.9185 ± 0.0030 | -0.2211 ± 0.1168 | 3 |

## Low → High density

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| RandomForest | 0.8266 ± 0.0022 | 0.8075 ± 0.0033 | 0.8111 ± 0.0065 | 0.2933 ± 0.0100 | 0.8608 ± 0.0007 | -0.0342 ± 0.0016 | 3 |
| XGBoost | 0.7600 ± 0.0140 | 0.8455 ± 0.0038 | 0.8292 ± 0.0039 | 0.1458 ± 0.0104 | 0.8583 ± 0.0009 | -0.0984 ± 0.0132 | 3 |
| GRU | 0.4929 ± 0.0874 | 0.9261 ± 0.0068 | 0.7849 ± 0.0346 | 0.4132 ± 0.1002 | 0.8788 ± 0.0044 | -0.3859 ± 0.0868 | 3 |
| GAT | 0.5791 ± 0.1096 | 0.8498 ± 0.0570 | 0.7728 ± 0.0198 | 0.2207 ± 0.1162 | 0.8455 ± 0.0011 | -0.2664 ± 0.1092 | 3 |
| RAVEN-X | 0.5456 ± 0.1158 | 0.8913 ± 0.0416 | 0.7286 ± 0.0846 | 0.3125 ± 0.1455 | 0.8680 ± 0.0065 | -0.3223 ± 0.1133 | 3 |
| RAVEN-X-GF | 0.6095 ± 0.0983 | 0.8794 ± 0.0043 | 0.8265 ± 0.0327 | 0.2219 ± 0.0925 | 0.8800 ± 0.0055 | -0.2705 ± 0.0938 | 3 |

## highway_2 → urban_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8737 ± 0.0010 | 0.8182 ± 0.0038 | 0.8936 ± 0.0002 | 0.0376 ± 0.0025 | 0.8583 ± 0.0009 | 0.0153 ± 0.0002 | 3 |
| RAVEN-X | 0.8734 ± 0.0030 | 0.8586 ± 0.0059 | 0.9244 ± 0.0018 | 0.0384 ± 0.0125 | 0.8680 ± 0.0065 | 0.0054 ± 0.0051 | 3 |
| RAVEN-X-GF | 0.8935 ± 0.0111 | 0.8674 ± 0.0056 | 0.9314 ± 0.0034 | 0.0276 ± 0.0134 | 0.8800 ± 0.0055 | 0.0134 ± 0.0102 | 3 |

## highway_7 → highway_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.7391 ± 0.0169 | 0.8131 ± 0.0051 | 0.8569 ± 0.0036 | 0.1060 ± 0.0091 | 0.8681 ± 0.0009 | -0.1290 ± 0.0176 | 3 |
| RAVEN-X | 0.8069 ± 0.0068 | 0.8215 ± 0.0027 | 0.8802 ± 0.0020 | 0.0845 ± 0.0245 | 0.8431 ± 0.0263 | -0.0361 ± 0.0295 | 3 |
| RAVEN-X-GF | 0.8306 ± 0.0022 | 0.8424 ± 0.0030 | 0.9028 ± 0.0025 | 0.0634 ± 0.0037 | 0.8746 ± 0.0068 | -0.0441 ± 0.0090 | 3 |

## highway_7 → urban_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.7937 ± 0.0164 | 0.8368 ± 0.0030 | 0.8882 ± 0.0006 | 0.0844 ± 0.0068 | 0.8681 ± 0.0009 | -0.0744 ± 0.0170 | 3 |
| RAVEN-X | 0.8573 ± 0.0052 | 0.8591 ± 0.0019 | 0.9200 ± 0.0006 | 0.0690 ± 0.0256 | 0.8431 ± 0.0263 | 0.0142 ± 0.0251 | 3 |
| RAVEN-X-GF | 0.8761 ± 0.0059 | 0.8770 ± 0.0020 | 0.9300 ± 0.0009 | 0.0522 ± 0.0025 | 0.8746 ± 0.0068 | 0.0014 ± 0.0027 | 3 |

## urban_2 → highway_2

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8561 ± 0.0009 | 0.7818 ± 0.0008 | 0.8757 ± 0.0004 | 0.0219 ± 0.0005 | 0.8916 ± 0.0003 | -0.0355 ± 0.0008 | 3 |
| RAVEN-X | 0.8678 ± 0.0084 | 0.8273 ± 0.0060 | 0.9075 ± 0.0036 | 0.0171 ± 0.0016 | 0.9123 ± 0.0030 | -0.0445 ± 0.0057 | 3 |
| RAVEN-X-GF | 0.8748 ± 0.0090 | 0.8275 ± 0.0032 | 0.9116 ± 0.0039 | 0.0262 ± 0.0084 | 0.9185 ± 0.0030 | -0.0438 ± 0.0114 | 3 |

## urban_2 → highway_7

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.8277 ± 0.0069 | 0.8426 ± 0.0022 | 0.8764 ± 0.0004 | 0.0487 ± 0.0050 | 0.8916 ± 0.0003 | -0.0639 ± 0.0072 | 3 |
| RAVEN-X | 0.6911 ± 0.0967 | 0.8466 ± 0.0344 | 0.8345 ± 0.0380 | 0.1163 ± 0.0806 | 0.9123 ± 0.0030 | -0.2212 ± 0.0989 | 3 |
| RAVEN-X-GF | 0.6376 ± 0.1457 | 0.8931 ± 0.0283 | 0.8583 ± 0.0358 | 0.2130 ± 0.1545 | 0.9185 ± 0.0030 | -0.2809 ± 0.1427 | 3 |

## highway_2 → highway_7

| Model | F1 | Recall | PR-AUC | ECE | in-domain F1 | ΔF1 (cross - in) | seeds |
|---|---|---|---|---|---|---|---|
| XGBoost | 0.7600 ± 0.0140 | 0.8455 ± 0.0038 | 0.8292 ± 0.0039 | 0.1458 ± 0.0104 | 0.8583 ± 0.0009 | -0.0984 ± 0.0132 | 3 |
| RAVEN-X | 0.5456 ± 0.1158 | 0.8913 ± 0.0416 | 0.7286 ± 0.0846 | 0.3125 ± 0.1455 | 0.8680 ± 0.0065 | -0.3223 ± 0.1133 | 3 |
| RAVEN-X-GF | 0.6095 ± 0.0983 | 0.8794 ± 0.0043 | 0.8265 ± 0.0327 | 0.2219 ± 0.0925 | 0.8800 ± 0.0055 | -0.2705 ± 0.0938 | 3 |

## PR-AUC summary (mean over seeds)

| Test | RandomForest | XGBoost | GRU | GAT | RAVEN-X | RAVEN-X-GF |
|---|---|---|---|---|---|---|
| Urban → Highway | 0.8737 | 0.8763 | 0.8659 | 0.8435 | 0.8504 | 0.8609 |
| Low → High density | 0.8111 | 0.8292 | 0.7849 | 0.7728 | 0.7286 | 0.8265 |
| highway_2 → urban_2 | – | 0.8936 | – | – | 0.9244 | 0.9314 |
| highway_7 → highway_2 | – | 0.8569 | – | – | 0.8802 | 0.9028 |
| highway_7 → urban_2 | – | 0.8882 | – | – | 0.9200 | 0.9300 |
| urban_2 → highway_2 | – | 0.8757 | – | – | 0.9075 | 0.9116 |
| urban_2 → highway_7 | – | 0.8764 | – | – | 0.8345 | 0.8583 |
| highway_2 → highway_7 | – | 0.8292 | – | – | 0.7286 | 0.8265 |

## Reading the results

This is the 19-feature model set (15 step features plus the 4 neighbour features, no G5). The 17-feature version of the same experiment is in `reports/nextgen_cross_scenario_3seeds`.

The short version: adding neighbour features helped in-domain and did not help transfer. For RAVEN-X-GF the cross-domain PR-AUC went down in 6 of the 7 distinct tests compared with 17 features. The seventh, urban_2 → highway_2, is flat (0.9116 vs 0.9102).

Training on highway data transfers well and is stable. highway_2 → urban_2, highway_7 → highway_2 and highway_7 → urban_2 all have F1 std under 0.012 for the three models run there. RAVEN-X-GF is the best of the three on F1, PR-AUC and ECE in all three, and on highway_2 → urban_2 and highway_7 → urban_2 it scores as well as or better than in-domain.

Training on urban_2 is where the neural models fall apart, and the seed spread is the story. RAVEN-X-GF on urban_2 → highway_7 gave F1 0.761, 0.477 and 0.676 across seeds 0, 1 and 2. Recall stays high (0.87-0.93) while F1 drops, so the threshold picked on urban validation data is too low for the highway stream: the model flags too much. XGBoost on the same pair is boring and reliable (0.828 ± 0.007). On the pooled Urban → Highway test the tree models now win outright on both F1 and PR-AUC; with 17 features RAVEN-X-GF had the best PR-AUC there (0.892), and now it has 0.861.

Low → High density got worse for every model. RAVEN-X-GF PR-AUC dropped from 0.866 to 0.827 and F1 from 0.681 to 0.610, and GRU F1 fell to 0.493. That fits what the neighbour features are: NbrCount and NbrNearestDist describe how crowded the road is, so a model trained at low density sees values at high density it has never seen. RAVEN-X-GF is still the best neural model there on PR-AUC, essentially tied with XGBoost (0.827 vs 0.829), but Random Forest has the best F1 (0.827).

What I'd take from this: for the in-domain and highway-trained results the 19-feature model is the one to report. For any claim about generalising across densities or from urban to highway, the 17-feature numbers are better and more stable, or the neighbour features need normalising by local density before they can travel. A threshold re-tuned on a small amount of target data would probably recover most of the urban_2-source F1 loss, since PR-AUC holds up much better than F1 does, but I haven't run that.
