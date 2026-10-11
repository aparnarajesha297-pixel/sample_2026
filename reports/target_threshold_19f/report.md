# Threshold re-tuning on target data

Seeds [0, 1, 2], 20 slice draws per budget. Budget = share of target receiver files labelled in every attack run (at least one). All F1 values are on the target receivers outside the slice, mean ± std over seeds (each seed first averaged over draws). *Source* is the threshold from source validation, *oracle* the best threshold for the held-out receivers themselves; both are shown on the held-out receivers of the 10% budget. Gains in the last table are paired (same held-out receivers for tuned and source).

## Urban → Highway

| Model | source | tuned 1% | tuned 5% | tuned 10% | tuned 20% | oracle |
|---|---|---|---|---|---|---|
| RandomForest | 0.8446 ± 0.0039 | 0.8550 ± 0.0008 | 0.8551 ± 0.0012 | 0.8568 ± 0.0007 | 0.8565 ± 0.0030 | 0.8571 ± 0.0008 |
| XGBoost | 0.8382 ± 0.0039 | 0.8443 ± 0.0011 | 0.8438 ± 0.0014 | 0.8459 ± 0.0009 | 0.8456 ± 0.0022 | 0.8465 ± 0.0007 |
| GRU | 0.7601 ± 0.0510 | 0.8088 ± 0.0245 | 0.8132 ± 0.0224 | 0.8147 ± 0.0227 | 0.8149 ± 0.0213 | 0.8155 ± 0.0227 |
| GAT | 0.7571 ± 0.0453 | 0.7892 ± 0.0263 | 0.7892 ± 0.0252 | 0.7925 ± 0.0232 | 0.7932 ± 0.0223 | 0.7938 ± 0.0225 |
| RAVEN-X | 0.7442 ± 0.0717 | 0.7601 ± 0.0558 | 0.7660 ± 0.0553 | 0.7685 ± 0.0546 | 0.7693 ± 0.0590 | 0.7715 ± 0.0543 |
| RAVEN-X-GF | 0.6992 ± 0.1204 | 0.7793 ± 0.0496 | 0.7825 ± 0.0500 | 0.7861 ± 0.0496 | 0.7863 ± 0.0480 | 0.7875 ± 0.0492 |

Slice size: 1% → 90 receivers / 99,037 steps, 5% → 375 receivers / 128,409 steps, 10% → 750 receivers / 248,649 steps, 20% → 1485 receivers / 418,877 steps

## Low → High density

| Model | source | tuned 1% | tuned 5% | tuned 10% | tuned 20% | oracle |
|---|---|---|---|---|---|---|
| RandomForest | 0.8280 ± 0.0039 | 0.8247 ± 0.0023 | 0.8291 ± 0.0035 | 0.8311 ± 0.0036 | 0.8309 ± 0.0052 | 0.8320 ± 0.0036 |
| XGBoost | 0.7618 ± 0.0128 | 0.7706 ± 0.0088 | 0.7771 ± 0.0021 | 0.7825 ± 0.0030 | 0.7829 ± 0.0105 | 0.7851 ± 0.0021 |
| GRU | 0.4953 ± 0.0878 | 0.7481 ± 0.0266 | 0.7526 ± 0.0218 | 0.7567 ± 0.0205 | 0.7546 ± 0.0303 | 0.7581 ± 0.0208 |
| GAT | 0.5817 ± 0.1093 | 0.7140 ± 0.0424 | 0.7182 ± 0.0354 | 0.7231 ± 0.0331 | 0.7243 ± 0.0379 | 0.7298 ± 0.0297 |
| RAVEN-X | 0.5482 ± 0.1185 | 0.6732 ± 0.1115 | 0.6723 ± 0.1235 | 0.6795 ± 0.1182 | 0.6758 ± 0.1153 | 0.6917 ± 0.1013 |
| RAVEN-X-GF | 0.6118 ± 0.1011 | 0.8006 ± 0.0436 | 0.8032 ± 0.0476 | 0.8065 ± 0.0467 | 0.8073 ± 0.0388 | 0.8074 ± 0.0461 |

Slice size: 1% → 15 receivers / 98,270 steps, 5% → 15 receivers / 89,350 steps, 10% → 30 receivers / 181,748 steps, 20% → 45 receivers / 291,310 steps

## highway_2 → urban_2

| Model | source | tuned 1% | tuned 5% | tuned 10% | tuned 20% | oracle |
|---|---|---|---|---|---|---|
| XGBoost | 0.8736 ± 0.0009 | 0.8758 ± 0.0010 | 0.8767 ± 0.0011 | 0.8768 ± 0.0013 | 0.8769 ± 0.0005 | 0.8771 ± 0.0013 |
| RAVEN-X | 0.8733 ± 0.0026 | 0.8758 ± 0.0038 | 0.8776 ± 0.0030 | 0.8779 ± 0.0028 | 0.8782 ± 0.0031 | 0.8787 ± 0.0027 |
| RAVEN-X-GF | 0.8935 ± 0.0107 | 0.8977 ± 0.0087 | 0.8991 ± 0.0089 | 0.8993 ± 0.0085 | 0.8994 ± 0.0093 | 0.8999 ± 0.0083 |

Slice size: 1% → 30 receivers / 13,008 steps, 5% → 120 receivers / 50,955 steps, 10% → 240 receivers / 103,173 steps, 20% → 465 receivers / 198,047 steps

## urban_2 → highway_2

| Model | source | tuned 1% | tuned 5% | tuned 10% | tuned 20% | oracle |
|---|---|---|---|---|---|---|
| XGBoost | 0.8558 ± 0.0012 | 0.8588 ± 0.0007 | 0.8601 ± 0.0006 | 0.8599 ± 0.0009 | 0.8600 ± 0.0009 | 0.8601 ± 0.0008 |
| RAVEN-X | 0.8676 ± 0.0086 | 0.8671 ± 0.0081 | 0.8692 ± 0.0087 | 0.8691 ± 0.0087 | 0.8694 ± 0.0083 | 0.8696 ± 0.0085 |
| RAVEN-X-GF | 0.8745 ± 0.0087 | 0.8737 ± 0.0092 | 0.8750 ± 0.0097 | 0.8750 ± 0.0095 | 0.8753 ± 0.0095 | 0.8755 ± 0.0095 |

Slice size: 1% → 75 receivers / 7,410 steps, 5% → 360 receivers / 35,582 steps, 10% → 720 receivers / 71,055 steps, 20% → 1440 receivers / 141,282 steps

## urban_2 → highway_7

| Model | source | tuned 1% | tuned 5% | tuned 10% | tuned 20% | oracle |
|---|---|---|---|---|---|---|
| XGBoost | 0.8291 ± 0.0053 | 0.8325 ± 0.0040 | 0.8363 ± 0.0015 | 0.8378 ± 0.0009 | 0.8389 ± 0.0050 | 0.8397 ± 0.0016 |
| RAVEN-X | 0.6931 ± 0.0985 | 0.7399 ± 0.0451 | 0.7433 ± 0.0487 | 0.7479 ± 0.0457 | 0.7503 ± 0.0394 | 0.7527 ± 0.0472 |
| RAVEN-X-GF | 0.6400 ± 0.1451 | 0.7830 ± 0.0410 | 0.7863 ± 0.0396 | 0.7900 ± 0.0386 | 0.7903 ± 0.0373 | 0.7918 ± 0.0381 |

Slice size: 1% → 15 receivers / 98,270 steps, 5% → 15 receivers / 89,350 steps, 10% → 30 receivers / 181,748 steps, 20% → 45 receivers / 291,310 steps

## F1 gain over the source threshold

| Test | Model | source F1 | Δ 1% | Δ 5% | Δ 10% | Δ 20% | Δ oracle |
|---|---|---|---|---|---|---|---|
| Urban → Highway | RandomForest | 0.8446 | +0.0111 | +0.0120 | +0.0122 | +0.0123 | +0.0125 |
| Urban → Highway | XGBoost | 0.8382 | +0.0066 | +0.0072 | +0.0077 | +0.0079 | +0.0083 |
| Urban → Highway | GRU | 0.7601 | +0.0478 | +0.0546 | +0.0546 | +0.0556 | +0.0554 |
| Urban → Highway | GAT | 0.7571 | +0.0319 | +0.0339 | +0.0354 | +0.0366 | +0.0367 |
| Urban → Highway | RAVEN-X | 0.7442 | +0.0152 | +0.0233 | +0.0243 | +0.0257 | +0.0272 |
| Urban → Highway | RAVEN-X-GF | 0.6992 | +0.0784 | +0.0852 | +0.0869 | +0.0882 | +0.0883 |
| Low → High density | RandomForest | 0.8280 | +0.0005 | +0.0024 | +0.0031 | +0.0030 | +0.0040 |
| Low → High density | XGBoost | 0.7618 | +0.0132 | +0.0172 | +0.0207 | +0.0211 | +0.0233 |
| Low → High density | GRU | 0.4953 | +0.2577 | +0.2601 | +0.2614 | +0.2591 | +0.2628 |
| Low → High density | GAT | 0.5817 | +0.1379 | +0.1402 | +0.1414 | +0.1417 | +0.1481 |
| Low → High density | RAVEN-X | 0.5482 | +0.1306 | +0.1270 | +0.1313 | +0.1275 | +0.1435 |
| Low → High density | RAVEN-X-GF | 0.6118 | +0.1940 | +0.1942 | +0.1947 | +0.1947 | +0.1956 |
| highway_2 → urban_2 | XGBoost | 0.8736 | +0.0023 | +0.0029 | +0.0032 | +0.0032 | +0.0035 |
| highway_2 → urban_2 | RAVEN-X | 0.8733 | +0.0025 | +0.0044 | +0.0045 | +0.0049 | +0.0054 |
| highway_2 → urban_2 | RAVEN-X-GF | 0.8935 | +0.0043 | +0.0058 | +0.0059 | +0.0060 | +0.0064 |
| urban_2 → highway_2 | XGBoost | 0.8558 | +0.0029 | +0.0040 | +0.0041 | +0.0042 | +0.0043 |
| urban_2 → highway_2 | RAVEN-X | 0.8676 | -0.0006 | +0.0014 | +0.0015 | +0.0018 | +0.0020 |
| urban_2 → highway_2 | RAVEN-X-GF | 0.8745 | -0.0010 | +0.0003 | +0.0005 | +0.0008 | +0.0009 |
| urban_2 → highway_7 | XGBoost | 0.8291 | +0.0069 | +0.0085 | +0.0087 | +0.0098 | +0.0106 |
| urban_2 → highway_7 | RAVEN-X | 0.6931 | +0.0513 | +0.0525 | +0.0547 | +0.0563 | +0.0595 |
| urban_2 → highway_7 | RAVEN-X-GF | 0.6400 | +0.1481 | +0.1494 | +0.1500 | +0.1498 | +0.1519 |

