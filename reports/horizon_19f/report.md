# Mobility-aware planning horizon (row 15)

Beliefs: `results/svoi_hw2_nbr/beliefs.npz`. Estimators and SVoI tables fitted on validation; 123,620 test episodes per row. Range R = 320 m (99th percentile of receiver distance on validation); 40.1% of test steps have a receding sender.

## 1. Estimating time left (test, seconds, capped at 120 s)

| Estimator | Steps | MAE (s) | RMSE (s) | Bias (s) | n |
|---|---|---|---|---|---|
| constant | all | 10.2131 | 14.8175 | -2.2818 | 703520 |
| constant | benign | 10.2056 | 15.0470 | -3.1500 | 564575 |
| constant | attacker | 10.2437 | 13.8457 | 1.2463 | 138945 |
| constant | true time left ≤ 10 s | 7.2955 | 7.8965 | 7.2955 | 380960 |
| age | all | 10.1589 | 14.9405 | -2.0494 | 703520 |
| age | benign | 10.7946 | 15.4041 | -2.2502 | 564575 |
| age | attacker | 7.5757 | 12.8864 | -1.2335 | 138945 |
| age | true time left ≤ 10 s | 7.5292 | 8.7399 | 6.8712 | 380960 |
| geometric | all | 15.6382 | 29.6160 | 5.1241 | 703520 |
| geometric | benign | 16.7225 | 30.7564 | 5.5903 | 564575 |
| geometric | attacker | 11.2326 | 24.4408 | 3.2298 | 138945 |
| geometric | true time left ≤ 10 s | 10.5044 | 23.9982 | 9.7729 | 380960 |

## 2. Fixed vs mobility-aware horizon (test)

The oracle uses the true steps left in the stream. It is an upper bound only: it is not available at runtime and it leaks the label (one-message streams are almost all Sybil ghosts).

| Evidence | H | Horizon | F1 | Precision | Recall | PR-AUC | Evidence cost | Error cost | Total cost | Observations | Horizon shrunk at start (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a1-a4 | 1 | fixed H | 0.9526 | 0.9288 | 0.9777 | 0.9896 | 1.1878 | 1.5719 | 2.7597 | 1.0000 | nan |
| a1-a4 | 1 | constant | 0.9526 | 0.9288 | 0.9777 | 0.9896 | 1.1878 | 1.5719 | 2.7597 | 1.0000 | 0.0000 |
| a1-a4 | 1 | age | 0.9282 | 0.9464 | 0.9107 | 0.9741 | 0.1622 | 4.2001 | 4.3623 | 1.0000 | 64.7994 |
| a1-a4 | 1 | geometric | 0.9281 | 0.9464 | 0.9105 | 0.9740 | 0.1595 | 4.2097 | 4.3692 | 1.0000 | 65.9618 |
| a1-a4 | 1 | oracle (true steps left) | 0.9514 | 0.9286 | 0.9754 | 0.9897 | 1.1535 | 1.6696 | 2.8232 | 1.0000 | 35.3503 |
| a1-a4 | 2 | fixed H | 0.9812 | 0.9862 | 0.9762 | 0.9922 | 1.4982 | 1.1197 | 2.6179 | 1.0000 | nan |
| a1-a4 | 2 | constant | 0.9812 | 0.9862 | 0.9762 | 0.9922 | 1.4982 | 1.1197 | 2.6179 | 1.0000 | 0.0000 |
| a1-a4 | 2 | age | 0.9300 | 0.9501 | 0.9108 | 0.9745 | 0.1840 | 4.1647 | 4.3487 | 1.0000 | 64.7994 |
| a1-a4 | 2 | geometric | 0.9298 | 0.9500 | 0.9105 | 0.9744 | 0.1817 | 4.1773 | 4.3591 | 1.0000 | 66.9964 |
| a1-a4 | 2 | oracle (true steps left) | 0.9796 | 0.9843 | 0.9749 | 0.9925 | 1.4555 | 1.1882 | 2.6437 | 1.0000 | 37.9348 |
| a1-a4 | 3 | fixed H | 0.9766 | 0.9817 | 0.9715 | 0.9916 | 1.2872 | 1.3548 | 2.6420 | 1.1199 | nan |
| a1-a4 | 3 | constant | 0.9766 | 0.9817 | 0.9715 | 0.9916 | 1.2872 | 1.3548 | 2.6420 | 1.1199 | 0.0000 |
| a1-a4 | 3 | age | 0.9289 | 0.9484 | 0.9101 | 0.9738 | 0.1750 | 4.2063 | 4.3813 | 1.0168 | 64.7994 |
| a1-a4 | 3 | geometric | 0.9290 | 0.9487 | 0.9101 | 0.9739 | 0.1740 | 4.2035 | 4.3776 | 1.0164 | 67.6921 |
| a1-a4 | 3 | oracle (true steps left) | 0.9760 | 0.9814 | 0.9706 | 0.9917 | 1.2680 | 1.3927 | 2.6606 | 1.1153 | 40.1796 |
| a1-a4 | 5 | fixed H | 0.9687 | 0.9790 | 0.9586 | 0.9898 | 1.2769 | 1.9104 | 3.1872 | 1.1340 | nan |
| a1-a4 | 5 | constant | 0.9687 | 0.9790 | 0.9586 | 0.9898 | 1.2769 | 1.9104 | 3.1872 | 1.1340 | 0.0000 |
| a1-a4 | 5 | age | 0.9283 | 0.9479 | 0.9096 | 0.9738 | 0.1772 | 4.2283 | 4.4055 | 1.0230 | 64.7994 |
| a1-a4 | 5 | geometric | 0.9288 | 0.9487 | 0.9097 | 0.9740 | 0.1773 | 4.2184 | 4.3958 | 1.0227 | 69.5947 |
| a1-a4 | 5 | oracle (true steps left) | 0.9693 | 0.9809 | 0.9578 | 0.9895 | 1.2645 | 1.9270 | 3.1915 | 1.1283 | 45.6399 |
| a1-a4 | 10 | fixed H | 0.9663 | 0.9773 | 0.9555 | 0.9887 | 1.2936 | 2.0555 | 3.3491 | 1.1631 | nan |
| a1-a4 | 10 | constant | 0.9663 | 0.9773 | 0.9555 | 0.9887 | 1.2936 | 2.0555 | 3.3491 | 1.1631 | 0.0000 |
| a1-a4 | 10 | age | 0.9280 | 0.9476 | 0.9091 | 0.9737 | 0.1851 | 4.2525 | 4.4376 | 1.0392 | 73.3781 |
| a1-a4 | 10 | geometric | 0.9280 | 0.9478 | 0.9090 | 0.9736 | 0.1853 | 4.2553 | 4.4406 | 1.0380 | 77.1679 |
| a1-a4 | 10 | oracle (true steps left) | 0.9680 | 0.9812 | 0.9552 | 0.9889 | 1.2876 | 2.0359 | 3.3235 | 1.1547 | 64.7994 |
| a1 only | 1 | fixed H | 0.9517 | 0.9548 | 0.9486 | 0.9831 | 0.3293 | 2.5491 | 2.8784 | 1.3293 | nan |
| a1 only | 1 | constant | 0.9517 | 0.9548 | 0.9486 | 0.9831 | 0.3293 | 2.5491 | 2.8784 | 1.3293 | 0.0000 |
| a1 only | 1 | age | 0.9242 | 0.9410 | 0.9079 | 0.9722 | 0.0242 | 4.3614 | 4.3856 | 1.0242 | 64.7994 |
| a1 only | 1 | geometric | 0.9242 | 0.9410 | 0.9079 | 0.9722 | 0.0242 | 4.3614 | 4.3856 | 1.0242 | 65.9618 |
| a1 only | 1 | oracle (true steps left) | 0.9517 | 0.9548 | 0.9486 | 0.9831 | 0.3293 | 2.5491 | 2.8784 | 1.3293 | 35.3503 |
| a1 only | 2 | fixed H | 0.9521 | 0.9533 | 0.9510 | 0.9835 | 0.4344 | 2.4632 | 2.8976 | 1.4344 | nan |
| a1 only | 2 | constant | 0.9521 | 0.9533 | 0.9510 | 0.9835 | 0.4344 | 2.4632 | 2.8976 | 1.4344 | 0.0000 |
| a1 only | 2 | age | 0.9247 | 0.9422 | 0.9079 | 0.9723 | 0.0411 | 4.3530 | 4.3942 | 1.0411 | 64.7994 |
| a1 only | 2 | geometric | 0.9247 | 0.9422 | 0.9079 | 0.9723 | 0.0411 | 4.3538 | 4.3949 | 1.0411 | 66.9964 |
| a1 only | 2 | oracle (true steps left) | 0.9521 | 0.9533 | 0.9510 | 0.9835 | 0.4344 | 2.4632 | 2.8976 | 1.4344 | 37.9348 |
| a1 only | 3 | fixed H | 0.9546 | 0.9575 | 0.9517 | 0.9837 | 0.4991 | 2.3952 | 2.8943 | 1.4991 | nan |
| a1 only | 3 | constant | 0.9546 | 0.9575 | 0.9517 | 0.9837 | 0.4991 | 2.3952 | 2.8943 | 1.4991 | 0.0000 |
| a1 only | 3 | age | 0.9244 | 0.9415 | 0.9080 | 0.9723 | 0.0548 | 4.3580 | 4.4128 | 1.0548 | 64.7994 |
| a1 only | 3 | geometric | 0.9244 | 0.9415 | 0.9079 | 0.9723 | 0.0547 | 4.3588 | 4.4135 | 1.0547 | 67.6921 |
| a1 only | 3 | oracle (true steps left) | 0.9546 | 0.9575 | 0.9517 | 0.9837 | 0.4991 | 2.3952 | 2.8943 | 1.4991 | 40.1796 |
| a1 only | 5 | fixed H | 0.9566 | 0.9608 | 0.9524 | 0.9838 | 0.5844 | 2.3406 | 2.9249 | 1.5844 | nan |
| a1 only | 5 | constant | 0.9566 | 0.9608 | 0.9524 | 0.9838 | 0.5844 | 2.3406 | 2.9249 | 1.5844 | 0.0000 |
| a1 only | 5 | age | 0.9250 | 0.9426 | 0.9080 | 0.9724 | 0.0756 | 4.3474 | 4.4230 | 1.0756 | 64.7994 |
| a1 only | 5 | geometric | 0.9249 | 0.9423 | 0.9080 | 0.9724 | 0.0754 | 4.3495 | 4.4248 | 1.0754 | 69.5947 |
| a1 only | 5 | oracle (true steps left) | 0.9566 | 0.9608 | 0.9524 | 0.9838 | 0.5844 | 2.3406 | 2.9249 | 1.5844 | 45.6399 |
| a1 only | 10 | fixed H | 0.9614 | 0.9707 | 0.9523 | 0.9839 | 0.6699 | 2.2595 | 2.9295 | 1.6699 | nan |
| a1 only | 10 | constant | 0.9614 | 0.9707 | 0.9523 | 0.9839 | 0.6699 | 2.2595 | 2.9295 | 1.6699 | 0.0000 |
| a1 only | 10 | age | 0.9264 | 0.9456 | 0.9079 | 0.9726 | 0.1060 | 4.3266 | 4.4326 | 1.1060 | 73.3781 |
| a1 only | 10 | geometric | 0.9261 | 0.9451 | 0.9079 | 0.9726 | 0.1048 | 4.3304 | 4.4352 | 1.1048 | 77.1679 |
| a1 only | 10 | oracle (true steps left) | 0.9614 | 0.9707 | 0.9523 | 0.9839 | 0.6699 | 2.2595 | 2.9295 | 1.6699 | 64.7994 |
| a1-a4 | 1 | validation-chosen (age, q = 0.5, min cap 1) | 0.9526 | 0.9288 | 0.9777 | 0.9896 | 1.1878 | 1.5719 | 2.7597 | 1.0000 | 0.0000 |
| a1-a4 | 1 | oracle, min cap 1 | 0.9526 | 0.9288 | 0.9777 | 0.9896 | 1.1878 | 1.5719 | 2.7597 | 1.0000 | 0.0000 |
| a1-a4 | 2 | validation-chosen (age, q = 0.5, min cap 1) | 0.9812 | 0.9862 | 0.9762 | 0.9922 | 1.4982 | 1.1197 | 2.6179 | 1.0000 | 64.7994 |
| a1-a4 | 2 | oracle, min cap 1 | 0.9812 | 0.9862 | 0.9762 | 0.9922 | 1.4982 | 1.1197 | 2.6179 | 1.0000 | 37.9348 |
| a1-a4 | 3 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.9811 | 0.9858 | 0.9765 | 0.9926 | 1.4963 | 1.1105 | 2.6068 | 1.0164 | 67.6921 |
| a1-a4 | 3 | oracle, min cap 1 | 0.9781 | 0.9835 | 0.9727 | 0.9920 | 1.3089 | 1.2894 | 2.5984 | 1.1153 | 40.1796 |
| a1-a4 | 5 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.9807 | 0.9860 | 0.9754 | 0.9922 | 1.4992 | 1.1530 | 2.6523 | 1.0225 | 69.5947 |
| a1-a4 | 5 | oracle, min cap 1 | 0.9715 | 0.9833 | 0.9599 | 0.9897 | 1.3073 | 1.8204 | 3.1277 | 1.1286 | 45.6399 |
| a1-a4 | 10 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.9801 | 0.9850 | 0.9753 | 0.9919 | 1.5072 | 1.1670 | 2.6742 | 1.0380 | 77.1679 |
| a1-a4 | 10 | oracle, min cap 1 | 0.9701 | 0.9829 | 0.9576 | 0.9893 | 1.3300 | 1.9207 | 3.2507 | 1.1549 | 64.7994 |
| a1 only | 1 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9517 | 0.9548 | 0.9486 | 0.9831 | 0.3292 | 2.5491 | 2.8783 | 1.3292 | 1.1624 |
| a1 only | 2 | validation-chosen (age, q = 0.5, min cap 1) | 0.9521 | 0.9533 | 0.9510 | 0.9835 | 0.4344 | 2.4632 | 2.8976 | 1.4344 | 64.7994 |
| a1 only | 2 | oracle, min cap 1 | 0.9521 | 0.9533 | 0.9510 | 0.9835 | 0.4344 | 2.4632 | 2.8976 | 1.4344 | 37.9348 |
| a1 only | 3 | validation-chosen (age, q = 0.5, min cap 1) | 0.9546 | 0.9575 | 0.9517 | 0.9837 | 0.4991 | 2.3952 | 2.8943 | 1.4991 | 64.7994 |
| a1 only | 3 | oracle, min cap 1 | 0.9546 | 0.9575 | 0.9517 | 0.9837 | 0.4991 | 2.3952 | 2.8943 | 1.4991 | 40.1796 |
| a1 only | 5 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9564 | 0.9606 | 0.9523 | 0.9838 | 0.5832 | 2.3451 | 2.9283 | 1.5832 | 4.7953 |
| a1 only | 10 | validation-chosen (age, q = 0.5, min cap 1) | 0.9614 | 0.9707 | 0.9523 | 0.9839 | 0.6699 | 2.2595 | 2.9295 | 1.6699 | 73.3781 |
| a1 only | 10 | oracle, min cap 1 | 0.9614 | 0.9707 | 0.9523 | 0.9839 | 0.6699 | 2.2595 | 2.9295 | 1.6699 | 64.7994 |

## Validation choice

Chosen per H and evidence set by the lowest total cost on a validation replay; the test rows above labelled 'validation-chosen' use exactly this choice.

| Evidence | H | Estimator | q | Min cap | Validation total cost | Validation total cost, fixed H |
|---|---|---|---|---|---|---|
| a1-a4 | 1 | age | 0.5000 | 1 | 2.2840 | 2.2840 |
| a1-a4 | 2 | age | 0.5000 | 1 | 2.1760 | 2.1760 |
| a1-a4 | 3 | geometric | 0.5000 | 1 | 2.1632 | 2.2083 |
| a1-a4 | 5 | geometric | 0.5000 | 1 | 2.2144 | 2.6458 |
| a1-a4 | 10 | geometric | 0.5000 | 1 | 2.2105 | 2.7669 |
| a1 only | 1 | geometric | 0.7500 | 0 | 2.4046 | 2.4062 |
| a1 only | 2 | age | 0.5000 | 1 | 2.3680 | 2.3680 |
| a1 only | 3 | age | 0.5000 | 1 | 2.3625 | 2.3625 |
| a1 only | 5 | geometric | 0.7500 | 0 | 2.3016 | 2.3016 |
| a1 only | 10 | age | 0.5000 | 1 | 2.3160 | 2.3160 |

## Change vs fixed H

| Evidence | H | Horizon | ΔF1 | ΔTotal cost | ΔEvidence cost |
|---|---|---|---|---|---|
| a1-a4 | 1 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 1 | age | -0.0244 | 1.6025 | -1.0257 |
| a1-a4 | 1 | geometric | -0.0246 | 1.6094 | -1.0284 |
| a1-a4 | 1 | oracle (true steps left) | -0.0012 | 0.0634 | -0.0343 |
| a1-a4 | 2 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 2 | age | -0.0511 | 1.7307 | -1.3142 |
| a1-a4 | 2 | geometric | -0.0513 | 1.7411 | -1.3165 |
| a1-a4 | 2 | oracle (true steps left) | -0.0016 | 0.0257 | -0.0427 |
| a1-a4 | 3 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 3 | age | -0.0477 | 1.7393 | -1.1121 |
| a1-a4 | 3 | geometric | -0.0476 | 1.7356 | -1.1131 |
| a1-a4 | 3 | oracle (true steps left) | -0.0006 | 0.0186 | -0.0192 |
| a1-a4 | 5 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 5 | age | -0.0404 | 1.2182 | -1.0997 |
| a1-a4 | 5 | geometric | -0.0399 | 1.2085 | -1.0995 |
| a1-a4 | 5 | oracle (true steps left) | 0.0006 | 0.0043 | -0.0123 |
| a1-a4 | 10 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 10 | age | -0.0383 | 1.0885 | -1.1085 |
| a1-a4 | 10 | geometric | -0.0383 | 1.0915 | -1.1083 |
| a1-a4 | 10 | oracle (true steps left) | 0.0017 | -0.0256 | -0.0060 |
| a1 only | 1 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 1 | age | -0.0275 | 1.5073 | -0.3050 |
| a1 only | 1 | geometric | -0.0275 | 1.5073 | -0.3051 |
| a1 only | 1 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 2 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 2 | age | -0.0274 | 1.4965 | -0.3933 |
| a1 only | 2 | geometric | -0.0274 | 1.4973 | -0.3934 |
| a1 only | 2 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 3 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 3 | age | -0.0302 | 1.5185 | -0.4443 |
| a1 only | 3 | geometric | -0.0302 | 1.5192 | -0.4444 |
| a1 only | 3 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 5 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 5 | age | -0.0316 | 1.4980 | -0.5088 |
| a1 only | 5 | geometric | -0.0317 | 1.4999 | -0.5090 |
| a1 only | 5 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 10 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 10 | age | -0.0350 | 1.5031 | -0.5640 |
| a1 only | 10 | geometric | -0.0353 | 1.5057 | -0.5651 |
| a1 only | 10 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 1 | validation-chosen (age, q = 0.5, min cap 1) | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 1 | oracle, min cap 1 | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 2 | validation-chosen (age, q = 0.5, min cap 1) | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 2 | oracle, min cap 1 | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 3 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.0045 | -0.0352 | 0.2091 |
| a1-a4 | 3 | oracle, min cap 1 | 0.0015 | -0.0436 | 0.0218 |
| a1-a4 | 5 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.0120 | -0.5350 | 0.2224 |
| a1-a4 | 5 | oracle, min cap 1 | 0.0028 | -0.0596 | 0.0304 |
| a1-a4 | 10 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.0138 | -0.6749 | 0.2136 |
| a1-a4 | 10 | oracle, min cap 1 | 0.0038 | -0.0984 | 0.0364 |
| a1 only | 1 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.0000 | -0.0000 | -0.0000 |
| a1 only | 2 | validation-chosen (age, q = 0.5, min cap 1) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 2 | oracle, min cap 1 | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 3 | validation-chosen (age, q = 0.5, min cap 1) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 3 | oracle, min cap 1 | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 5 | validation-chosen (geometric, q = 0.75, min cap 0) | -0.0001 | 0.0034 | -0.0011 |
| a1 only | 10 | validation-chosen (age, q = 0.5, min cap 1) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 10 | oracle, min cap 1 | 0.0000 | 0.0000 | 0.0000 |
## Reading the results (19-feature RAVEN-X-GF)

The conclusion is the same as with 17 features:
- **No estimator of time left beats a constant** (MAE about 10 s;
  geometric 15.6 s).
- **The median estimators used as a cap hurt.** Cost rises to about 4.4
  because every new stream gets decided with no evidence.
- **The validation-chosen cap fixes long horizons.** Total cost goes from
  3.19 to 2.65 at H = 5 and from 3.35 to 2.67 at H = 10. But it barely
  beats the best fixed horizon (H = 2, 2.62; capped H = 3 is 2.61).
- **A rule with no mobility content does the same.** "Plan one step at a
  stream's first message" matches the cap to within 0.01 (diagnosis.md).
  The gain is a correction of the passive-transition model at stream
  starts, not a mobility effect.
- **With passive observation only, the horizon changes nothing.**
