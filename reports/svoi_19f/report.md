# SVoI controller (nextgen data)

Detector RAVEN-X-GF, temperature T = 0.741 fitted on validation (single-step PR-AUC of the calibrated belief on test: 0.9201). Costs: C_FA = 100, C_FR = 20; SVoI evidence actions: a1, a2, a3, a4; costs a1..a4 = 1 / 2 / 3 / 5; check reliabilities a2..a4 = 0.80 / 0.90 / 0.99 (assumed); gamma = 1; criticality K = 1. Grid, p(b), transitions and the policy are fitted on validation; 123,620 test episodes per row.

Lower total cost is better (evidence spent + cost of wrong decisions).

| H | Policy | F1 | Precision | Recall | Evidence cost | Error cost | Total cost | Observations | Queries | Decided at once (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SVoI | 0.9526 | 0.9288 | 0.9777 | 1.1878 | 1.5719 | 2.7597 | 1.0000 | 0.3705 | 62.9453 |
| 1 | Never-query | 0.9234 | 0.9398 | 0.9075 | 0.0000 | 4.3896 | 4.3896 | 1.0000 | 0.0000 | 100.0000 |
| 1 | Always-query | 0.9542 | 0.9604 | 0.9481 | 0.6465 | 2.5179 | 3.1644 | 1.6465 | 0.6465 | 35.3503 |
| 1 | Fixed-interval | 0.9542 | 0.9604 | 0.9481 | 0.6465 | 2.5179 | 3.1644 | 1.6465 | 0.6465 | 35.3503 |
| 1 | Random | 0.9344 | 0.9276 | 0.9413 | 1.3361 | 3.0940 | 4.4301 | 1.0811 | 0.4584 | 54.1579 |
| 2 | SVoI | 0.9812 | 0.9862 | 0.9762 | 1.4982 | 1.1197 | 2.6179 | 1.0000 | 0.4341 | 62.9453 |
| 2 | Never-query | 0.9234 | 0.9398 | 0.9075 | 0.0000 | 4.3896 | 4.3896 | 1.0000 | 0.0000 | 100.0000 |
| 2 | Always-query | 0.9531 | 0.9547 | 0.9516 | 1.2671 | 2.4247 | 3.6918 | 2.2671 | 1.2671 | 35.3503 |
| 2 | Fixed-interval | 0.9409 | 0.9214 | 0.9612 | 1.9395 | 2.3276 | 4.2671 | 1.6465 | 1.2930 | 35.3503 |
| 2 | Random | 0.9392 | 0.9380 | 0.9404 | 1.9508 | 3.0372 | 4.9880 | 1.1205 | 0.6703 | 54.1482 |
| 3 | SVoI | 0.9766 | 0.9817 | 0.9715 | 1.2872 | 1.3548 | 2.6420 | 1.1199 | 0.4946 | 63.2543 |
| 3 | Never-query | 0.9234 | 0.9398 | 0.9075 | 0.0000 | 4.3896 | 4.3896 | 1.0000 | 0.0000 | 100.0000 |
| 3 | Always-query | 0.9560 | 0.9581 | 0.9538 | 1.8654 | 2.3035 | 4.1689 | 2.8654 | 1.8654 | 35.3503 |
| 3 | Fixed-interval | 0.9526 | 0.9530 | 0.9521 | 2.5601 | 2.4184 | 4.9785 | 2.2671 | 1.9136 | 35.3503 |
| 3 | Random | 0.9410 | 0.9398 | 0.9422 | 2.2377 | 2.9452 | 5.1828 | 1.1410 | 0.7703 | 54.2016 |
| 5 | SVoI | 0.9687 | 0.9790 | 0.9586 | 1.2769 | 1.9104 | 3.1872 | 1.1340 | 0.5287 | 63.1095 |
| 5 | Never-query | 0.9234 | 0.9398 | 0.9075 | 0.0000 | 4.3896 | 4.3896 | 1.0000 | 0.0000 | 100.0000 |
| 5 | Always-query | 0.9587 | 0.9598 | 0.9576 | 2.9811 | 2.1356 | 5.1166 | 3.9811 | 2.9811 | 35.3503 |
| 5 | Fixed-interval | 0.9552 | 0.9559 | 0.9545 | 4.3997 | 2.2946 | 6.6943 | 2.8654 | 3.1325 | 35.3503 |
| 5 | Random | 0.9413 | 0.9396 | 0.9430 | 2.4367 | 2.9162 | 5.3529 | 1.1556 | 0.8395 | 54.2202 |

## SVoI: vehicles decided after k observations

| observations used | H=1 | H=2 | H=3 | H=5 |
|---|---|---|---|---|
| 1 | 123620 | 123620 | 108793 | 110915 |
| 2 | 0 | 0 | 14827 | 9864 |
| 3 | 0 | 0 | 0 | 1824 |
| 4 | 0 | 0 | 0 | 1017 |

## SVoI step by step (H = 5; row 12)

Cumulative over vehicles decided after at most k observations; 'Decided at k' are vehicles whose decision used exactly k observations, and the attack rate / F1 of that group show how hard those cases were.

| Observations | Decided (%) | F1 | Recall | Precision | False-positive rate | Decided at k | Attack rate at k | F1 at k |
|---|---|---|---|---|---|---|---|---|
| 1 | 89.7225 | 0.9793 | 0.9755 | 0.9831 | 0.0125 | 110915 | 0.4278 | 0.9793 |
| 2 | 97.7018 | 0.9702 | 0.9606 | 0.9801 | 0.0142 | 9864 | 0.3450 | 0.8311 |
| 3 | 99.1773 | 0.9688 | 0.9585 | 0.9793 | 0.0148 | 1824 | 0.4293 | 0.8718 |
| 4 | 100.0000 | 0.9687 | 0.9586 | 0.9790 | 0.0149 | 1017 | 0.2763 | 0.9514 |
## Reading the results (19-feature RAVEN-X-GF)

- **SVoI has the lowest total cost at every horizon:** 2.76 / 2.62 / 2.64 /
  3.19 for H = 1 / 2 / 3 / 5. The next best is Always-query at H = 1 (3.16),
  and the gap widens with H (5.12 vs 3.19 at H = 5). Never-query costs 4.39.
- **SVoI decides 63% of vehicles at once** and still reaches F1 0.981 at
  H = 2, with fewer than half a query per vehicle.
- **Longer horizons get slightly worse after H = 2.** This is the stream-start
  effect diagnosed in row 15 (see horizon_19f): the waiting model is too
  optimistic at a stream's first message.
- **Passive observation only (svoi_passive_19f):** SVoI has the lowest total
  cost at every H (2.88–2.92). It matches Always-query's F1 (0.952–0.957 vs
  0.953–0.959) with 2–5× less evidence.
