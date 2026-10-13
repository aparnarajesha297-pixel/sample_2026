# Mobility-aware planning horizon (row 15)

Beliefs: `results/svoi_hw2/beliefs.npz`. Estimators and SVoI tables fitted on validation; 123,620 test episodes per row. Range R = 320 m (99th percentile of receiver distance on validation); 40.1% of test steps have a receding sender.

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
| a1-a4 | 1 | fixed H | 0.9432 | 0.9080 | 0.9812 | 0.9885 | 1.2571 | 1.6316 | 2.8887 | 1.0000 | nan |
| a1-a4 | 1 | constant | 0.9432 | 0.9080 | 0.9812 | 0.9885 | 1.2571 | 1.6316 | 2.8887 | 1.0000 | 0.0000 |
| a1-a4 | 1 | age | 0.8523 | 0.7742 | 0.9480 | 0.9747 | 0.2338 | 4.5229 | 4.7567 | 1.0000 | 64.7994 |
| a1-a4 | 1 | geometric | 0.8524 | 0.7743 | 0.9478 | 0.9746 | 0.2290 | 4.5287 | 4.7577 | 1.0000 | 65.9618 |
| a1-a4 | 1 | oracle (true steps left) | 0.9398 | 0.9027 | 0.9800 | 0.9881 | 1.2198 | 1.7334 | 2.9532 | 1.0000 | 35.3503 |
| a1-a4 | 2 | fixed H | 0.9442 | 0.9103 | 0.9807 | 0.9901 | 1.3180 | 1.6277 | 2.9458 | 1.2675 | nan |
| a1-a4 | 2 | constant | 0.9442 | 0.9103 | 0.9807 | 0.9901 | 1.3180 | 1.6277 | 2.9458 | 1.2675 | 0.0000 |
| a1-a4 | 2 | age | 0.8532 | 0.7758 | 0.9476 | 0.9749 | 0.2668 | 4.5148 | 4.7816 | 1.0166 | 64.7994 |
| a1-a4 | 2 | geometric | 0.8531 | 0.7758 | 0.9476 | 0.9746 | 0.2631 | 4.5172 | 4.7803 | 1.0160 | 66.9964 |
| a1-a4 | 2 | oracle (true steps left) | 0.9449 | 0.9122 | 0.9801 | 0.9899 | 1.3098 | 1.6347 | 2.9445 | 1.2608 | 37.9348 |
| a1-a4 | 3 | fixed H | 0.9445 | 0.9117 | 0.9797 | 0.9905 | 1.3785 | 1.6543 | 3.0327 | 1.3293 | nan |
| a1-a4 | 3 | constant | 0.9445 | 0.9117 | 0.9797 | 0.9905 | 1.3785 | 1.6543 | 3.0327 | 1.3293 | 0.0000 |
| a1-a4 | 3 | age | 0.8524 | 0.7748 | 0.9475 | 0.9747 | 0.2676 | 4.5376 | 4.8052 | 1.0265 | 64.7994 |
| a1-a4 | 3 | geometric | 0.8531 | 0.7759 | 0.9474 | 0.9746 | 0.2668 | 4.5240 | 4.7909 | 1.0258 | 67.6921 |
| a1-a4 | 3 | oracle (true steps left) | 0.9464 | 0.9155 | 0.9794 | 0.9908 | 1.3764 | 1.6324 | 3.0088 | 1.3214 | 40.1796 |
| a1-a4 | 5 | fixed H | 0.9435 | 0.9108 | 0.9787 | 0.9902 | 1.4151 | 1.7049 | 3.1200 | 1.3899 | nan |
| a1-a4 | 5 | constant | 0.9435 | 0.9108 | 0.9787 | 0.9902 | 1.4151 | 1.7049 | 3.1200 | 1.3899 | 0.0000 |
| a1-a4 | 5 | age | 0.8525 | 0.7750 | 0.9472 | 0.9745 | 0.2743 | 4.5434 | 4.8177 | 1.0355 | 64.7994 |
| a1-a4 | 5 | geometric | 0.8531 | 0.7760 | 0.9473 | 0.9747 | 0.2733 | 4.5287 | 4.8020 | 1.0353 | 69.5947 |
| a1-a4 | 5 | oracle (true steps left) | 0.9463 | 0.9164 | 0.9784 | 0.9902 | 1.4196 | 1.6654 | 3.0850 | 1.3801 | 45.6399 |
| a1-a4 | 10 | fixed H | 0.9430 | 0.9103 | 0.9780 | 0.9899 | 1.4438 | 1.7392 | 3.1830 | 1.4336 | nan |
| a1-a4 | 10 | constant | 0.9430 | 0.9103 | 0.9780 | 0.9899 | 1.4438 | 1.7392 | 3.1830 | 1.4336 | 0.0000 |
| a1-a4 | 10 | age | 0.8522 | 0.7746 | 0.9470 | 0.9744 | 0.2781 | 4.5569 | 4.8350 | 1.0433 | 73.3781 |
| a1-a4 | 10 | geometric | 0.8528 | 0.7757 | 0.9469 | 0.9743 | 0.2794 | 4.5467 | 4.8261 | 1.0429 | 77.1679 |
| a1-a4 | 10 | oracle (true steps left) | 0.9473 | 0.9189 | 0.9776 | 0.9902 | 1.4570 | 1.6735 | 3.1305 | 1.4224 | 64.7994 |
| a1 only | 1 | fixed H | 0.9234 | 0.8926 | 0.9564 | 0.9826 | 0.3267 | 2.8122 | 3.1389 | 1.3267 | nan |
| a1 only | 1 | constant | 0.9234 | 0.8926 | 0.9564 | 0.9826 | 0.3267 | 2.8122 | 3.1389 | 1.3267 | 0.0000 |
| a1 only | 1 | age | 0.8501 | 0.7733 | 0.9437 | 0.9727 | 0.0318 | 4.7068 | 4.7387 | 1.0318 | 64.7994 |
| a1 only | 1 | geometric | 0.8501 | 0.7733 | 0.9437 | 0.9727 | 0.0317 | 4.7067 | 4.7384 | 1.0317 | 65.9618 |
| a1 only | 1 | oracle (true steps left) | 0.9234 | 0.8926 | 0.9564 | 0.9826 | 0.3267 | 2.8122 | 3.1389 | 1.3267 | 35.3503 |
| a1 only | 2 | fixed H | 0.9273 | 0.8984 | 0.9581 | 0.9829 | 0.4386 | 2.6844 | 3.1230 | 1.4386 | nan |
| a1 only | 2 | constant | 0.9273 | 0.8984 | 0.9581 | 0.9829 | 0.4386 | 2.6844 | 3.1230 | 1.4386 | 0.0000 |
| a1 only | 2 | age | 0.8511 | 0.7749 | 0.9437 | 0.9728 | 0.0506 | 4.6860 | 4.7366 | 1.0506 | 64.7994 |
| a1 only | 2 | geometric | 0.8511 | 0.7750 | 0.9437 | 0.9728 | 0.0504 | 4.6858 | 4.7363 | 1.0504 | 66.9964 |
| a1 only | 2 | oracle (true steps left) | 0.9273 | 0.8984 | 0.9581 | 0.9829 | 0.4386 | 2.6844 | 3.1230 | 1.4386 | 37.9348 |
| a1 only | 3 | fixed H | 0.9324 | 0.9079 | 0.9582 | 0.9831 | 0.5343 | 2.5886 | 3.1228 | 1.5343 | nan |
| a1 only | 3 | constant | 0.9324 | 0.9079 | 0.9582 | 0.9831 | 0.5343 | 2.5886 | 3.1228 | 1.5343 | 0.0000 |
| a1 only | 3 | age | 0.8511 | 0.7751 | 0.9437 | 0.9728 | 0.0843 | 4.6881 | 4.7724 | 1.0843 | 64.7994 |
| a1 only | 3 | geometric | 0.8511 | 0.7751 | 0.9437 | 0.9728 | 0.0836 | 4.6894 | 4.7729 | 1.0836 | 67.6921 |
| a1 only | 3 | oracle (true steps left) | 0.9324 | 0.9079 | 0.9582 | 0.9831 | 0.5331 | 2.5902 | 3.1233 | 1.5331 | 40.1796 |
| a1 only | 5 | fixed H | 0.9405 | 0.9217 | 0.9601 | 0.9837 | 0.7562 | 2.3807 | 3.1369 | 1.7562 | nan |
| a1 only | 5 | constant | 0.9405 | 0.9217 | 0.9601 | 0.9837 | 0.7562 | 2.3807 | 3.1369 | 1.7562 | 0.0000 |
| a1 only | 5 | age | 0.8523 | 0.7768 | 0.9440 | 0.9731 | 0.1219 | 4.6567 | 4.7786 | 1.1219 | 64.7994 |
| a1 only | 5 | geometric | 0.8523 | 0.7768 | 0.9439 | 0.9730 | 0.1205 | 4.6588 | 4.7793 | 1.1205 | 69.5947 |
| a1 only | 5 | oracle (true steps left) | 0.9406 | 0.9220 | 0.9600 | 0.9836 | 0.7501 | 2.3821 | 3.1322 | 1.7501 | 45.6399 |
| a1 only | 10 | fixed H | 0.9466 | 0.9328 | 0.9608 | 0.9839 | 0.9362 | 2.2482 | 3.1844 | 1.9362 | nan |
| a1 only | 10 | constant | 0.9466 | 0.9328 | 0.9608 | 0.9839 | 0.9362 | 2.2482 | 3.1844 | 1.9362 | 0.0000 |
| a1 only | 10 | age | 0.8526 | 0.7773 | 0.9441 | 0.9731 | 0.1624 | 4.6468 | 4.8092 | 1.1624 | 73.3781 |
| a1 only | 10 | geometric | 0.8527 | 0.7774 | 0.9440 | 0.9731 | 0.1605 | 4.6476 | 4.8081 | 1.1605 | 77.1679 |
| a1 only | 10 | oracle (true steps left) | 0.9468 | 0.9334 | 0.9606 | 0.9838 | 0.9202 | 2.2503 | 3.1705 | 1.9202 | 64.7994 |
| a1-a4 | 1 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9431 | 0.9081 | 0.9809 | 0.9879 | 1.2523 | 1.6423 | 2.8946 | 1.0000 | 1.1624 |
| a1-a4 | 2 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.9683 | 0.9561 | 0.9808 | 0.9917 | 1.5550 | 1.1865 | 2.7416 | 1.0161 | 66.9964 |
| a1-a4 | 2 | oracle, min cap 1 | 0.9478 | 0.9169 | 0.9808 | 0.9908 | 1.3521 | 1.5585 | 2.9105 | 1.2610 | 37.9348 |
| a1-a4 | 3 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.9689 | 0.9577 | 0.9803 | 0.9916 | 1.5655 | 1.1974 | 2.7629 | 1.0255 | 67.6921 |
| a1-a4 | 3 | oracle, min cap 1 | 0.9498 | 0.9214 | 0.9801 | 0.9911 | 1.4202 | 1.5449 | 2.9651 | 1.3209 | 40.1796 |
| a1-a4 | 5 | validation-chosen (age, q = 0.5, min cap 1) | 0.9682 | 0.9567 | 0.9799 | 0.9914 | 1.5665 | 1.2215 | 2.7880 | 1.0357 | 64.7994 |
| a1-a4 | 5 | oracle, min cap 1 | 0.9501 | 0.9225 | 0.9793 | 0.9908 | 1.4636 | 1.5667 | 3.0303 | 1.3804 | 45.6399 |
| a1-a4 | 10 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.9686 | 0.9575 | 0.9800 | 0.9916 | 1.5775 | 1.2092 | 2.7867 | 1.0421 | 77.1679 |
| a1-a4 | 10 | oracle, min cap 1 | 0.9506 | 0.9241 | 0.9786 | 0.9903 | 1.5004 | 1.5800 | 3.0804 | 1.4217 | 64.7994 |
| a1 only | 1 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9234 | 0.8926 | 0.9564 | 0.9826 | 0.3266 | 2.8120 | 3.1386 | 1.3266 | 1.1624 |
| a1 only | 2 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9274 | 0.8987 | 0.9581 | 0.9829 | 0.4377 | 2.6834 | 3.1211 | 1.4377 | 2.1971 |
| a1 only | 3 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9325 | 0.9082 | 0.9582 | 0.9831 | 0.5322 | 2.5866 | 3.1188 | 1.5322 | 2.8927 |
| a1 only | 5 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.9407 | 0.9222 | 0.9599 | 0.9836 | 0.7517 | 2.3844 | 3.1361 | 1.7517 | 4.7953 |
| a1 only | 10 | validation-chosen (geometric, q = 0.75, min cap 1) | 0.9466 | 0.9331 | 0.9606 | 0.9839 | 0.9296 | 2.2556 | 3.1852 | 1.9296 | 8.6046 |
| a1 only | 10 | oracle, min cap 1 | 0.9468 | 0.9334 | 0.9606 | 0.9838 | 0.9202 | 2.2503 | 3.1705 | 1.9202 | 64.7994 |

## Validation choice

Chosen per H and evidence set by the lowest total cost on a validation replay; the test rows above labelled 'validation-chosen' use exactly this choice.

| Evidence | H | Estimator | q | Min cap | Validation total cost | Validation total cost, fixed H |
|---|---|---|---|---|---|---|
| a1-a4 | 1 | geometric | 0.7500 | 0 | 2.3263 | 2.3321 |
| a1-a4 | 2 | geometric | 0.5000 | 1 | 2.2001 | 2.3822 |
| a1-a4 | 3 | geometric | 0.5000 | 1 | 2.1758 | 2.4182 |
| a1-a4 | 5 | age | 0.5000 | 1 | 2.1993 | 2.4166 |
| a1-a4 | 10 | geometric | 0.5000 | 1 | 2.2272 | 2.4836 |
| a1 only | 1 | geometric | 0.7500 | 0 | 2.3174 | 2.3191 |
| a1 only | 2 | geometric | 0.7500 | 0 | 2.3052 | 2.3092 |
| a1 only | 3 | geometric | 0.7500 | 0 | 2.3518 | 2.3556 |
| a1 only | 5 | geometric | 0.7500 | 0 | 2.3494 | 2.3529 |
| a1 only | 10 | geometric | 0.7500 | 1 | 2.3864 | 2.3974 |

## Change vs fixed H

| Evidence | H | Horizon | ΔF1 | ΔTotal cost | ΔEvidence cost |
|---|---|---|---|---|---|
| a1-a4 | 1 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 1 | age | -0.0909 | 1.8680 | -1.0233 |
| a1-a4 | 1 | geometric | -0.0908 | 1.8690 | -1.0281 |
| a1-a4 | 1 | oracle (true steps left) | -0.0034 | 0.0645 | -0.0373 |
| a1-a4 | 2 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 2 | age | -0.0910 | 1.8359 | -1.0512 |
| a1-a4 | 2 | geometric | -0.0911 | 1.8346 | -1.0549 |
| a1-a4 | 2 | oracle (true steps left) | 0.0007 | -0.0013 | -0.0083 |
| a1-a4 | 3 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 3 | age | -0.0920 | 1.7725 | -1.1109 |
| a1-a4 | 3 | geometric | -0.0914 | 1.7581 | -1.1116 |
| a1-a4 | 3 | oracle (true steps left) | 0.0019 | -0.0239 | -0.0021 |
| a1-a4 | 5 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 5 | age | -0.0910 | 1.6977 | -1.1408 |
| a1-a4 | 5 | geometric | -0.0904 | 1.6821 | -1.1418 |
| a1-a4 | 5 | oracle (true steps left) | 0.0028 | -0.0350 | 0.0045 |
| a1-a4 | 10 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1-a4 | 10 | age | -0.0908 | 1.6520 | -1.1657 |
| a1-a4 | 10 | geometric | -0.0901 | 1.6431 | -1.1644 |
| a1-a4 | 10 | oracle (true steps left) | 0.0043 | -0.0525 | 0.0132 |
| a1 only | 1 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 1 | age | -0.0733 | 1.5998 | -0.2949 |
| a1 only | 1 | geometric | -0.0733 | 1.5995 | -0.2950 |
| a1 only | 1 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 2 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 2 | age | -0.0762 | 1.6136 | -0.3880 |
| a1 only | 2 | geometric | -0.0762 | 1.6133 | -0.3882 |
| a1 only | 2 | oracle (true steps left) | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 3 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 3 | age | -0.0813 | 1.6496 | -0.4499 |
| a1 only | 3 | geometric | -0.0813 | 1.6501 | -0.4507 |
| a1 only | 3 | oracle (true steps left) | -0.0000 | 0.0005 | -0.0012 |
| a1 only | 5 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 5 | age | -0.0882 | 1.6417 | -0.6343 |
| a1 only | 5 | geometric | -0.0883 | 1.6424 | -0.6357 |
| a1 only | 5 | oracle (true steps left) | 0.0001 | -0.0047 | -0.0061 |
| a1 only | 10 | constant | 0.0000 | 0.0000 | 0.0000 |
| a1 only | 10 | age | -0.0940 | 1.6248 | -0.7738 |
| a1 only | 10 | geometric | -0.0940 | 1.6238 | -0.7757 |
| a1 only | 10 | oracle (true steps left) | 0.0002 | -0.0139 | -0.0160 |
| a1-a4 | 1 | validation-chosen (geometric, q = 0.75, min cap 0) | -0.0001 | 0.0059 | -0.0048 |
| a1-a4 | 2 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.0241 | -0.2042 | 0.2370 |
| a1-a4 | 2 | oracle, min cap 1 | 0.0036 | -0.0352 | 0.0340 |
| a1-a4 | 3 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.0244 | -0.2698 | 0.1871 |
| a1-a4 | 3 | oracle, min cap 1 | 0.0053 | -0.0676 | 0.0418 |
| a1-a4 | 5 | validation-chosen (age, q = 0.5, min cap 1) | 0.0246 | -0.3320 | 0.1514 |
| a1-a4 | 5 | oracle, min cap 1 | 0.0065 | -0.0897 | 0.0485 |
| a1-a4 | 10 | validation-chosen (geometric, q = 0.5, min cap 1) | 0.0257 | -0.3963 | 0.1337 |
| a1-a4 | 10 | oracle, min cap 1 | 0.0076 | -0.1026 | 0.0566 |
| a1 only | 1 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.0000 | -0.0003 | -0.0001 |
| a1 only | 2 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.0001 | -0.0019 | -0.0009 |
| a1 only | 3 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.0001 | -0.0040 | -0.0021 |
| a1 only | 5 | validation-chosen (geometric, q = 0.75, min cap 0) | 0.0002 | -0.0008 | -0.0045 |
| a1 only | 10 | validation-chosen (geometric, q = 0.75, min cap 1) | 0.0000 | 0.0008 | -0.0066 |
| a1 only | 10 | oracle, min cap 1 | 0.0002 | -0.0139 | -0.0160 |
## Reading the results

- **Estimating time left is hard on this data.** No estimator gets below
  about 10 s MAE. The geometric one is the worst (15.6 s), because most
  streams end for reasons other than leaving range: a pseudonym change, the
  sender leaving the simulation, or a reception gap. See
  `reports/checks/rows15_16_verification.md`.
- **The median estimate is harmful as a cap.** For a new stream, the median
  time left is 0 s, because most one-message streams are Sybil ghosts. So
  every new vehicle gets decided with no evidence, and F1 falls to about
  0.85. Underestimating is costly and overestimating is free, which is why
  the quantile and a minimum cap are chosen on validation.
- **The validation-chosen cap helps when the controller can use active
  checks.** With a1–a4 and H ≥ 2, test F1 rises from 0.943–0.945 to
  0.968–0.969 and total cost falls 7–12% (e.g. 3.03 → 2.76 at H = 3). It
  also beats the best fixed horizon (H = 1, 2.89) by about 5%. With passive
  observation alone there is no effect.
- **The oracle barely helps.** The true time left, with a minimum cap of 1,
  lowers cost by 1–4%, which is less than the runtime estimate. That's the
  first sign the gain isn't about vehicles leaving range.
- **Where the gain comes from** (`diagnosis.md`): almost all of it is on
  episodes that start at a stream's first message (F1 0.956 → 0.984, cost
  3.09 → 2.70). With a fixed horizon, the controller waits at a new stream,
  expecting its belief to sharpen. The passive-transition model is pooled
  mostly from mid-stream steps, and it overstates how much one more message
  helps at a stream's start. The cap forces a one-step plan there, so the
  controller checks straight away. A rule with no mobility content ("plan
  one step on a stream's first message") reproduces the gain to within
  0.02 cost.

**Conclusion for row 15.** The mobility-aware horizon does lower cost, but
the time-left estimate itself contributes little. What it really corrects is
the passive-observation model at stream starts. On this evidence, the
learned time-left predictor the status document mentions isn't worth
building yet. A cheaper and more direct fix is to condition the a1
transition model on stream age. That's the natural next step, and it hasn't
been run.

Caveats: single detector (RAVEN-X-GF, seed 0) on highway_2; the reliabilities
of a2–a4 are assumed, as in rows 10–12.
