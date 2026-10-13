# Experiment 1 over 10 seeds

Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]. Each seed retrains every model from scratch; thresholds are chosen on validation, metrics are on the test split.

## Detection (mean ± std over seeds)

| Model | seeds | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|
| RandomForest | 10 | 0.9505 ± 0.0002 | 0.9663 ± 0.0033 | 0.7763 ± 0.0018 | 0.8610 ± 0.0005 | 0.9130 ± 0.0001 | 0.8807 ± 0.0001 |
| XGBoost | 10 | 0.9488 ± 0.0010 | 0.9500 ± 0.0106 | 0.7820 ± 0.0046 | 0.8578 ± 0.0018 | 0.9147 ± 0.0004 | 0.8811 ± 0.0004 |
| GRU | 10 | 0.9541 ± 0.0022 | 0.9282 ± 0.0128 | 0.8322 ± 0.0040 | 0.8775 ± 0.0051 | 0.9430 ± 0.0016 | 0.9163 ± 0.0018 |
| GAT | 10 | 0.9450 ± 0.0017 | 0.9428 ± 0.0155 | 0.7683 ± 0.0061 | 0.8465 ± 0.0034 | 0.9143 ± 0.0019 | 0.8783 ± 0.0016 |
| RAVEN-X | 10 | 0.9514 ± 0.0042 | 0.9192 ± 0.0229 | 0.8271 ± 0.0078 | 0.8705 ± 0.0097 | 0.9443 ± 0.0019 | 0.9154 ± 0.0036 |
| RAVEN-X-GF | 10 | 0.9551 ± 0.0029 | 0.9315 ± 0.0189 | 0.8346 ± 0.0056 | 0.8803 ± 0.0065 | 0.9443 ± 0.0009 | 0.9185 ± 0.0012 |

## F1 stability and calibration

| Model | F1 95% CI | F1 min–max | ECE | Brier |
|---|---|---|---|---|
| RandomForest | [0.8606, 0.8613] | 0.8602 – 0.8616 | 0.1265 ± 0.0005 | 0.0711 ± 0.0002 |
| XGBoost | [0.8565, 0.8592] | 0.8555 – 0.8606 | 0.0204 ± 0.0022 | 0.0485 ± 0.0007 |
| GRU | [0.8739, 0.8812] | 0.8677 – 0.8844 | 0.0258 ± 0.0076 | 0.0439 ± 0.0035 |
| GAT | [0.8441, 0.8490] | 0.8408 – 0.8514 | 0.0169 ± 0.0053 | 0.0497 ± 0.0019 |
| RAVEN-X | [0.8636, 0.8775] | 0.8536 – 0.8809 | 0.0315 ± 0.0128 | 0.0493 ± 0.0079 |
| RAVEN-X-GF | [0.8756, 0.8849] | 0.8701 – 0.8877 | 0.0215 ± 0.0074 | 0.0414 ± 0.0038 |

## Paired comparison on F1: RAVEN-X-GF vs each model

Positive Δ = the reference is better.

| vs | seeds | ΔF1 (ref − other) | 95% CI of Δ | ref wins | paired t p | Wilcoxon p | significant (p<0.05, both) |
|---|---|---|---|---|---|---|---|
| RandomForest | 10 | +0.0193 | [+0.0145, +0.0241] | 10/10 | 7.7e-06 | 0.002 | yes |
| XGBoost | 10 | +0.0224 | [+0.0184, +0.0264] | 10/10 | 4.6e-07 | 0.002 | yes |
| GRU | 10 | +0.0027 | [-0.0008, +0.0063] | 8/10 | 0.12 | 0.11 | no |
| GAT | 10 | +0.0337 | [+0.0290, +0.0385] | 10/10 | 6.1e-08 | 0.002 | yes |
| RAVEN-X | 10 | +0.0097 | [+0.0022, +0.0173] | 8/10 | 0.017 | 0.027 | yes |

## Paired comparison on PR-AUC: RAVEN-X-GF vs each model

Positive Δ = the reference is better.

| vs | seeds | ΔPR-AUC (ref − other) | 95% CI of Δ | ref wins | paired t p | Wilcoxon p | significant (p<0.05, both) |
|---|---|---|---|---|---|---|---|
| RandomForest | 10 | +0.0378 | [+0.0369, +0.0388] | 10/10 | 1.3e-14 | 0.002 | yes |
| XGBoost | 10 | +0.0375 | [+0.0366, +0.0383] | 10/10 | 3.9e-15 | 0.002 | yes |
| GRU | 10 | +0.0022 | [+0.0008, +0.0036] | 9/10 | 0.0058 | 0.014 | yes |
| GAT | 10 | +0.0402 | [+0.0387, +0.0417] | 10/10 | 4.1e-13 | 0.002 | yes |
| RAVEN-X | 10 | +0.0031 | [+0.0004, +0.0058] | 7/10 | 0.028 | 0.037 | yes |

## Paired comparison on ROC-AUC: RAVEN-X-GF vs each model

Positive Δ = the reference is better.

| vs | seeds | ΔROC-AUC (ref − other) | 95% CI of Δ | ref wins | paired t p | Wilcoxon p | significant (p<0.05, both) |
|---|---|---|---|---|---|---|---|
| RandomForest | 10 | +0.0313 | [+0.0306, +0.0320] | 10/10 | 4.8e-15 | 0.002 | yes |
| XGBoost | 10 | +0.0296 | [+0.0289, +0.0303] | 10/10 | 8.2e-15 | 0.002 | yes |
| GRU | 10 | +0.0013 | [+0.0003, +0.0023] | 8/10 | 0.017 | 0.037 | yes |
| GAT | 10 | +0.0300 | [+0.0283, +0.0317] | 10/10 | 2e-11 | 0.002 | yes |
| RAVEN-X | 10 | -0.0000 | [-0.0014, +0.0013] | 6/10 | 0.95 | 1 | no |

## Paired comparison on ECE: RAVEN-X-GF vs each model

Positive Δ = the reference is better (for ECE, lower is better, so Δ is other − ref).

| vs | seeds | ΔECE (ref − other) | 95% CI of Δ | ref wins | paired t p | Wilcoxon p | significant (p<0.05, both) |
|---|---|---|---|---|---|---|---|
| RandomForest | 10 | +0.1050 | [+0.0997, +0.1104] | 10/10 | 7.2e-12 | 0.002 | yes |
| XGBoost | 10 | -0.0011 | [-0.0062, +0.0039] | 6/10 | 0.63 | 1 | no |
| GRU | 10 | +0.0044 | [-0.0006, +0.0094] | 8/10 | 0.078 | 0.13 | no |
| GAT | 10 | -0.0046 | [-0.0121, +0.0030] | 4/10 | 0.2 | 0.23 | no |
| RAVEN-X | 10 | +0.0100 | [+0.0013, +0.0187] | 8/10 | 0.029 | 0.027 | yes |

## Attack-wise F1 (mean ± std over seeds)

| Attack | RandomForest | XGBoost | GRU | GAT | RAVEN-X | RAVEN-X-GF |
|---|---|---|---|---|---|---|
| Acceleration Multiplication | 0.828 ± 0.006 | 0.878 ± 0.012 | 0.742 ± 0.039 | 0.827 ± 0.017 | 0.675 ± 0.052 | 0.776 ± 0.034 |
| Constant Position Offset | 0.79 ± 0.0 | 0.777 ± 0.002 | 0.842 ± 0.009 | 0.762 ± 0.008 | 0.828 ± 0.019 | 0.845 ± 0.008 |
| Constant Speed Offset | 0.921 ± 0.002 | 0.917 ± 0.004 | 0.931 ± 0.01 | 0.921 ± 0.006 | 0.931 ± 0.008 | 0.936 ± 0.013 |
| Data Replay | 0.29 ± 0.004 | 0.323 ± 0.01 | 0.793 ± 0.012 | 0.301 ± 0.012 | 0.795 ± 0.014 | 0.786 ± 0.022 |
| DoS | 0.988 ± 0.001 | 0.98 ± 0.005 | 0.971 ± 0.007 | 0.984 ± 0.005 | 0.973 ± 0.009 | 0.976 ± 0.008 |
| Feigned Braking | 0.857 ± 0.003 | 0.909 ± 0.007 | 0.86 ± 0.017 | 0.892 ± 0.011 | 0.845 ± 0.034 | 0.866 ± 0.019 |
| Position Mirroring | 0.294 ± 0.007 | 0.272 ± 0.015 | 0.588 ± 0.022 | 0.277 ± 0.018 | 0.582 ± 0.02 | 0.616 ± 0.02 |
| Random Position Offset | 0.978 ± 0.001 | 0.972 ± 0.005 | 0.96 ± 0.006 | 0.969 ± 0.006 | 0.96 ± 0.01 | 0.961 ± 0.009 |
| Random Speed Offset | 0.95 ± 0.001 | 0.942 ± 0.003 | 0.934 ± 0.008 | 0.937 ± 0.007 | 0.931 ± 0.011 | 0.937 ± 0.009 |
| Reversed Heading | 0.955 ± 0.001 | 0.949 ± 0.004 | 0.936 ± 0.008 | 0.948 ± 0.005 | 0.932 ± 0.012 | 0.938 ± 0.009 |
| Sudden Constant Speed | 0.818 ± 0.006 | 0.78 ± 0.019 | 0.723 ± 0.026 | 0.724 ± 0.04 | 0.701 ± 0.045 | 0.734 ± 0.052 |
| Sudden Stop | 0.947 ± 0.003 | 0.929 ± 0.009 | 0.82 ± 0.078 | 0.722 ± 0.057 | 0.748 ± 0.062 | 0.792 ± 0.062 |
| Time Delay | 0.013 ± 0.001 | 0.019 ± 0.003 | 0.024 ± 0.008 | 0.015 ± 0.008 | 0.039 ± 0.011 | 0.018 ± 0.008 |
| Traffic Congestion Sybil | 0.997 ± 0.0 | 0.995 ± 0.001 | 0.991 ± 0.002 | 0.995 ± 0.002 | 0.989 ± 0.003 | 0.992 ± 0.003 |
| Zero Speed Report | 0.983 ± 0.001 | 0.968 ± 0.002 | 0.95 ± 0.007 | 0.966 ± 0.004 | 0.949 ± 0.01 | 0.954 ± 0.008 |

## Compared with the 17-feature table (reports/nextgen_highway2_10seeds)

Features changed from 17 (with G5 = RelativeSpeed, RelativeHeading) to 19
(G5 dropped, four neighbour-disagreement features added). Same seeds, same
models, same splits; this run also uses deterministic torch kernels.

| Model | F1 (17) | F1 (19) | Δ | PR-AUC (17) | PR-AUC (19) | ECE (17) | ECE (19) |
|---|---|---|---|---|---|---|---|
| RandomForest | 0.803 | 0.861 | +0.058 | 0.848 | 0.881 | 0.137 | 0.127 |
| XGBoost | 0.797 | 0.858 | +0.060 | 0.855 | 0.881 | 0.032 | 0.020 |
| GRU | 0.827 | 0.878 | +0.051 | 0.888 | 0.916 | 0.025 | 0.026 |
| GAT | 0.842 | 0.847 | +0.005 | 0.876 | 0.878 | 0.021 | 0.017 |
| RAVEN-X | 0.870 | 0.871 | +0.001 | 0.914 | 0.915 | 0.031 | 0.032 |
| RAVEN-X-GF | 0.876 | 0.880 | +0.004 | 0.918 | 0.919 | 0.034 | 0.022 |

## Reading the results

- The models without a graph gain most: RandomForest and XGBoost +0.06 F1,
  GRU +0.05. They had no neighbour information before; the graph models
  already had it on their edges and move by less than 0.005.
- **RAVEN-X-GF is still the best model on every aggregate metric, but its
  F1 lead over GRU is no longer significant**: +0.003 F1 (95% CI −0.001 to
  +0.006, 8/10 seeds, p = 0.12). On PR-AUC and ROC-AUC it still beats GRU
  significantly, by a small margin (+0.002 and +0.001). Much of its earlier
  0.049 F1 lead over GRU came from GRU having no view of the neighbours.
- It still beats RandomForest, XGBoost, GAT and RAVEN-X significantly on F1
  (by 0.019, 0.022, 0.034 and 0.010), and its ECE fell from 0.034 to 0.022.
- The tabular models are now the best on several attacks (DoS, Sudden
  Stop, Sudden Constant Speed, Zero Speed Report, Acceleration
  Multiplication, Feigned Braking); the sequence models stay far ahead on
  Data Replay and Position Mirroring, and no model detects Time Delay.
