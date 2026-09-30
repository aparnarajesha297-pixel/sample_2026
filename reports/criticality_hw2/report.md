# Criticality multiplier (row 16)

Beliefs: `results/svoi_hw2/beliefs.npz`. Critical step: sender within 100 m and time to collision below 10 s (closing speed from consecutive steps). 4.7% of the 123,620 test episodes start on a critical step. SVoI tables fitted on validation, one per Cm level. For each weight W, the controller without the multiplier (Cm = 1 everywhere) and with it (Cm = W on critical steps) are scored on the same objective: an error made on a critical step costs W times more (weighted error cost). Lower weighted total cost is better.

## Critical-step flag

| Split | Critical steps (%) | Attack rate, critical | Attack rate, other |
|---|---|---|---|
| validation | 7.5552 | 0.1507 | 0.2069 |
| test | 10.6138 | 0.1515 | 0.2030 |

## Results (test)

| Evidence | H | W | Controller | Episodes | F1 | Precision | Recall | PR-AUC | Queries | Evidence cost | Error cost | Weighted error cost | Weighted total cost | Decided at once (%) | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a1-a4 | 3 | 2.0000 | without multiplier | all | 0.9445 | 0.9117 | 0.9797 | 0.9905 | 0.6759 | 1.3785 | 1.6543 | 1.8117 | 3.1901 | 61.9786 | 123620 |
| a1-a4 | 3 | 2.0000 | without multiplier | critical at start | 0.8714 | 0.8562 | 0.8871 | 0.9143 | 0.2509 | 0.6062 | 2.0882 | 4.1015 | 4.7077 | 80.7699 | 5871 |
| a1-a4 | 3 | 2.0000 | without multiplier | not critical at start | 0.9457 | 0.9126 | 0.9813 | 0.9913 | 0.6970 | 1.4170 | 1.6326 | 1.6975 | 3.1145 | 61.0417 | 117749 |
| a1-a4 | 3 | 2.0000 | with multiplier (Cm = 2) | all | 0.9455 | 0.9133 | 0.9800 | 0.9910 | 0.6877 | 1.4264 | 1.6258 | 1.7602 | 3.1866 | 60.8728 | 123620 |
| a1-a4 | 3 | 2.0000 | with multiplier (Cm = 2) | critical at start | 0.8751 | 0.8396 | 0.9139 | 0.9380 | 0.5278 | 1.2550 | 1.7714 | 3.5156 | 4.7706 | 57.4859 | 5871 |
| a1-a4 | 3 | 2.0000 | with multiplier (Cm = 2) | not critical at start | 0.9467 | 0.9145 | 0.9812 | 0.9916 | 0.6957 | 1.4349 | 1.6185 | 1.6727 | 3.1077 | 61.0417 | 117749 |
| a1-a4 | 3 | 5.0000 | without multiplier | all | 0.9445 | 0.9117 | 0.9797 | 0.9905 | 0.6759 | 1.3785 | 1.6543 | 2.2839 | 3.6624 | 61.9786 | 123620 |
| a1-a4 | 3 | 5.0000 | without multiplier | critical at start | 0.8714 | 0.8562 | 0.8871 | 0.9143 | 0.2509 | 0.6062 | 2.0882 | 10.1414 | 10.7476 | 80.7699 | 5871 |
| a1-a4 | 3 | 5.0000 | without multiplier | not critical at start | 0.9457 | 0.9126 | 0.9813 | 0.9913 | 0.6970 | 1.4170 | 1.6326 | 1.8922 | 3.3091 | 61.0417 | 117749 |
| a1-a4 | 3 | 5.0000 | with multiplier (Cm = 5) | all | 0.9464 | 0.9142 | 0.9809 | 0.9913 | 0.7075 | 1.4897 | 1.5828 | 1.9600 | 3.4497 | 59.5430 | 123620 |
| a1-a4 | 3 | 5.0000 | with multiplier (Cm = 5) | critical at start | 0.8983 | 0.8567 | 0.9443 | 0.9560 | 0.9353 | 2.2453 | 1.2809 | 6.2817 | 8.5270 | 29.4839 | 5871 |
| a1-a4 | 3 | 5.0000 | with multiplier (Cm = 5) | not critical at start | 0.9472 | 0.9152 | 0.9815 | 0.9917 | 0.6962 | 1.4520 | 1.5978 | 1.7446 | 3.1966 | 61.0417 | 117749 |
| a1-a4 | 5 | 2.0000 | without multiplier | all | 0.9435 | 0.9108 | 0.9787 | 0.9902 | 0.7442 | 1.4151 | 1.7049 | 1.8719 | 3.2869 | 61.9786 | 123620 |
| a1-a4 | 5 | 2.0000 | without multiplier | critical at start | 0.8687 | 0.8531 | 0.8849 | 0.9120 | 0.2689 | 0.6115 | 2.1325 | 4.2173 | 4.8288 | 80.7699 | 5871 |
| a1-a4 | 5 | 2.0000 | without multiplier | not critical at start | 0.9448 | 0.9117 | 0.9803 | 0.9910 | 0.7679 | 1.4551 | 1.6836 | 1.7549 | 3.2101 | 61.0417 | 117749 |
| a1-a4 | 5 | 2.0000 | with multiplier (Cm = 2) | all | 0.9435 | 0.9103 | 0.9791 | 0.9904 | 0.7684 | 1.4624 | 1.6939 | 1.8351 | 3.2976 | 60.8728 | 123620 |
| a1-a4 | 5 | 2.0000 | with multiplier (Cm = 2) | critical at start | 0.8665 | 0.8284 | 0.9082 | 0.9319 | 0.6122 | 1.2875 | 1.8975 | 3.7132 | 5.0007 | 57.4859 | 5871 |
| a1-a4 | 5 | 2.0000 | with multiplier (Cm = 2) | not critical at start | 0.9448 | 0.9117 | 0.9803 | 0.9911 | 0.7762 | 1.4711 | 1.6838 | 1.7415 | 3.2126 | 61.0417 | 117749 |
| a1-a4 | 5 | 5.0000 | without multiplier | all | 0.9435 | 0.9108 | 0.9787 | 0.9902 | 0.7442 | 1.4151 | 1.7049 | 2.3728 | 3.7878 | 61.9786 | 123620 |
| a1-a4 | 5 | 5.0000 | without multiplier | critical at start | 0.8687 | 0.8531 | 0.8849 | 0.9120 | 0.2689 | 0.6115 | 2.1325 | 10.4718 | 11.0833 | 80.7699 | 5871 |
| a1-a4 | 5 | 5.0000 | without multiplier | not critical at start | 0.9448 | 0.9117 | 0.9803 | 0.9910 | 0.7679 | 1.4551 | 1.6836 | 1.9689 | 3.4241 | 61.0417 | 117749 |
| a1-a4 | 5 | 5.0000 | with multiplier (Cm = 5) | all | 0.9454 | 0.9130 | 0.9800 | 0.9910 | 0.7961 | 1.5277 | 1.6285 | 1.9683 | 3.4960 | 59.5430 | 123620 |
| a1-a4 | 5 | 5.0000 | with multiplier (Cm = 5) | critical at start | 0.8982 | 0.8536 | 0.9477 | 0.9584 | 1.0804 | 2.3143 | 1.2434 | 5.8763 | 8.1906 | 29.4839 | 5871 |
| a1-a4 | 5 | 5.0000 | with multiplier (Cm = 5) | not critical at start | 0.9462 | 0.9141 | 0.9806 | 0.9914 | 0.7819 | 1.4885 | 1.6477 | 1.7734 | 3.2619 | 61.0417 | 117749 |
| a1 only | 3 | 2.0000 | without multiplier | all | 0.9324 | 0.9079 | 0.9582 | 0.9831 | 0.5343 | 0.5343 | 2.5886 | 2.8457 | 3.3799 | 65.7911 | 123620 |
| a1 only | 3 | 2.0000 | without multiplier | critical at start | 0.8643 | 0.8725 | 0.8563 | 0.8973 | 0.2129 | 0.2129 | 2.4800 | 4.8135 | 5.0264 | 88.8264 | 5871 |
| a1 only | 3 | 2.0000 | without multiplier | not critical at start | 0.9335 | 0.9085 | 0.9599 | 0.9842 | 0.5503 | 0.5503 | 2.5940 | 2.7475 | 3.2978 | 64.6426 | 117749 |
| a1 only | 3 | 2.0000 | with multiplier (Cm = 2) | all | 0.9321 | 0.9073 | 0.9584 | 0.9831 | 0.5500 | 0.5500 | 2.5889 | 2.8314 | 3.3814 | 65.5986 | 123620 |
| a1 only | 3 | 2.0000 | with multiplier (Cm = 2) | critical at start | 0.8616 | 0.8641 | 0.8591 | 0.8972 | 0.3090 | 0.3090 | 2.4766 | 4.6909 | 4.9998 | 84.7726 | 5871 |
| a1 only | 3 | 2.0000 | with multiplier (Cm = 2) | not critical at start | 0.9333 | 0.9080 | 0.9600 | 0.9842 | 0.5620 | 0.5620 | 2.5945 | 2.7387 | 3.3007 | 64.6426 | 117749 |
| a1 only | 3 | 5.0000 | without multiplier | all | 0.9324 | 0.9079 | 0.9582 | 0.9831 | 0.5343 | 0.5343 | 2.5886 | 3.6169 | 4.1511 | 65.7911 | 123620 |
| a1 only | 3 | 5.0000 | without multiplier | critical at start | 0.8643 | 0.8725 | 0.8563 | 0.8973 | 0.2129 | 0.2129 | 2.4800 | 11.8140 | 12.0269 | 88.8264 | 5871 |
| a1 only | 3 | 5.0000 | without multiplier | not critical at start | 0.9335 | 0.9085 | 0.9599 | 0.9842 | 0.5503 | 0.5503 | 2.5940 | 3.2082 | 3.7585 | 64.6426 | 117749 |
| a1 only | 3 | 5.0000 | with multiplier (Cm = 5) | all | 0.9321 | 0.9071 | 0.9584 | 0.9832 | 0.5611 | 0.5611 | 2.5879 | 3.5211 | 4.0822 | 65.4312 | 123620 |
| a1 only | 3 | 5.0000 | with multiplier (Cm = 5) | critical at start | 0.8621 | 0.8641 | 0.8601 | 0.8972 | 0.4050 | 0.4050 | 2.4800 | 11.0100 | 11.4151 | 81.2468 | 5871 |
| a1 only | 3 | 5.0000 | with multiplier (Cm = 5) | not critical at start | 0.9332 | 0.9078 | 0.9601 | 0.9842 | 0.5689 | 0.5689 | 2.5933 | 3.1477 | 3.7166 | 64.6426 | 117749 |
| a1 only | 5 | 2.0000 | without multiplier | all | 0.9405 | 0.9217 | 0.9601 | 0.9837 | 0.7562 | 0.7562 | 2.3807 | 2.6151 | 3.3713 | 65.7911 | 123620 |
| a1 only | 5 | 2.0000 | without multiplier | critical at start | 0.8754 | 0.8933 | 0.8583 | 0.8985 | 0.3379 | 0.3379 | 2.3982 | 4.6023 | 4.9402 | 88.8264 | 5871 |
| a1 only | 5 | 2.0000 | without multiplier | not critical at start | 0.9416 | 0.9221 | 0.9618 | 0.9847 | 0.7771 | 0.7771 | 2.3798 | 2.5160 | 3.2931 | 64.6426 | 117749 |
| a1 only | 5 | 2.0000 | with multiplier (Cm = 2) | all | 0.9404 | 0.9214 | 0.9603 | 0.9837 | 0.7749 | 0.7749 | 2.3774 | 2.5884 | 3.3633 | 65.5986 | 123620 |
| a1 only | 5 | 2.0000 | with multiplier (Cm = 2) | critical at start | 0.8734 | 0.8857 | 0.8614 | 0.8989 | 0.4468 | 0.4468 | 2.3914 | 4.4592 | 4.9060 | 84.7726 | 5871 |
| a1 only | 5 | 2.0000 | with multiplier (Cm = 2) | not critical at start | 0.9415 | 0.9220 | 0.9619 | 0.9848 | 0.7912 | 0.7912 | 2.3768 | 2.4951 | 3.2864 | 64.6426 | 117749 |
| a1 only | 5 | 5.0000 | without multiplier | all | 0.9405 | 0.9217 | 0.9601 | 0.9837 | 0.7562 | 0.7562 | 2.3807 | 3.3184 | 4.0746 | 65.7911 | 123620 |
| a1 only | 5 | 5.0000 | without multiplier | critical at start | 0.8754 | 0.8933 | 0.8583 | 0.8985 | 0.3379 | 0.3379 | 2.3982 | 11.2144 | 11.5524 | 88.8264 | 5871 |
| a1 only | 5 | 5.0000 | without multiplier | not critical at start | 0.9416 | 0.9221 | 0.9618 | 0.9847 | 0.7771 | 0.7771 | 2.3798 | 2.9247 | 3.7018 | 64.6426 | 117749 |
| a1 only | 5 | 5.0000 | with multiplier (Cm = 5) | all | 0.9405 | 0.9214 | 0.9604 | 0.9838 | 0.7972 | 0.7972 | 2.3716 | 3.1346 | 3.9318 | 65.1367 | 123620 |
| a1 only | 5 | 5.0000 | with multiplier (Cm = 5) | critical at start | 0.8751 | 0.8858 | 0.8646 | 0.9008 | 0.6708 | 0.6708 | 2.3608 | 10.0187 | 10.6895 | 75.0468 | 5871 |
| a1 only | 5 | 5.0000 | with multiplier (Cm = 5) | not critical at start | 0.9416 | 0.9219 | 0.9621 | 0.9848 | 0.8035 | 0.8035 | 2.3722 | 2.7914 | 3.5948 | 64.6426 | 117749 |
## Reading the results

- **The flag.** 10.6% of test steps are critical, but only 4.7% of
  episodes start on one: a stream's first step has no closing speed yet, so
  it is never flagged. Attacks are rarer inside the flag (0.15) than outside
  (0.20).
- **With active checks (a1–a4), a strong multiplier does what it's meant
  to.** With W = Cm = 5, the controller makes about four times as many
  queries on critical episodes (0.25 → 0.94 at H = 3):
  - F1 on critical episodes rises from 0.871 to 0.898, and recall from 0.887
    to 0.944.
  - PR-AUC of the final belief rises from 0.914 to 0.956.
  - The weighted total cost on critical episodes falls 21% (10.75 → 8.53;
    26% at H = 5).
  - Over all episodes, the weighted total cost falls 6–8%, and F1 doesn't
    drop anywhere.
- **Cm = 2 isn't enough.** The controller queries about twice as often on
  critical episodes, but F1 barely moves and the weighted cost goes up
  slightly (4.71 → 4.77). The extra evidence costs about as much as the
  errors it prevents.
- **With passive observation only (a1), there is almost no effect.** Waiting
  for one more message on a close, fast-approaching vehicle rarely changes
  the belief enough. F1 stays flat, and only the weighted cost at W = 5
  improves a little (−5 to −7%).
- As designed, the multiplier never changes accept vs reject at the moment
  of stopping. All of the effect comes from gathering more evidence first.

**Conclusion for row 16.** The multiplier helps where it's meant to, as long
as the controller has an informative check to spend. A kinematic flag works
as a stand-in for the missing event flag, but it's built from claimed
positions, so an attacker can influence it.

Caveats: single detector (RAVEN-X-GF, seed 0) on highway_2; the reliabilities
of a2–a4 are assumed; the criticality level is assumed constant over the
planning horizon; about 5,900 critical-start episodes.
