# SVoI controller (nextgen data)

Detector RAVEN-X-GF, temperature T = 0.778 fitted on validation (single-step PR-AUC of the calibrated belief on test: 0.9204). Costs: C_FA = 100, C_FR = 20; SVoI evidence actions: a1; costs a1..a4 = 1 / 2 / 3 / 5; check reliabilities a2..a4 = 0.80 / 0.90 / 0.99 (assumed); gamma = 1; criticality K = 1. Grid, p(b), transitions and the policy are fitted on validation; 123,620 test episodes per row.

Lower total cost is better (evidence spent + cost of wrong decisions).

| H | Policy | F1 | Precision | Recall | Evidence cost | Error cost | Total cost | Observations | Queries | Decided at once (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SVoI | 0.9234 | 0.8926 | 0.9564 | 0.3267 | 2.8122 | 3.1389 | 1.3267 | 0.3267 | 67.3289 |
| 1 | Never-query | 0.8491 | 0.7716 | 0.9439 | 0.0000 | 4.7212 | 4.7212 | 1.0000 | 0.0000 | 100.0000 |
| 1 | Always-query | 0.9279 | 0.9016 | 0.9558 | 0.6465 | 2.7428 | 3.3893 | 1.6465 | 0.6465 | 35.3503 |
| 2 | SVoI | 0.9273 | 0.8984 | 0.9581 | 0.4386 | 2.6844 | 3.1230 | 1.4386 | 0.4386 | 67.3289 |
| 2 | Never-query | 0.8491 | 0.7716 | 0.9439 | 0.0000 | 4.7212 | 4.7212 | 1.0000 | 0.0000 | 100.0000 |
| 2 | Always-query | 0.9291 | 0.9013 | 0.9587 | 1.2671 | 2.6282 | 3.8954 | 2.2671 | 1.2671 | 35.3503 |
| 3 | SVoI | 0.9324 | 0.9079 | 0.9582 | 0.5343 | 2.5886 | 3.1228 | 1.5343 | 0.5343 | 65.7911 |
| 3 | Never-query | 0.8491 | 0.7716 | 0.9439 | 0.0000 | 4.7212 | 4.7212 | 1.0000 | 0.0000 | 100.0000 |
| 3 | Always-query | 0.9347 | 0.9105 | 0.9602 | 1.8654 | 2.4795 | 4.3449 | 2.8654 | 1.8654 | 35.3503 |
| 5 | SVoI | 0.9405 | 0.9217 | 0.9601 | 0.7562 | 2.3807 | 3.1369 | 1.7562 | 0.7562 | 65.7911 |
| 5 | Never-query | 0.8491 | 0.7716 | 0.9439 | 0.0000 | 4.7212 | 4.7212 | 1.0000 | 0.0000 | 100.0000 |
| 5 | Always-query | 0.9453 | 0.9283 | 0.9630 | 2.9811 | 2.1959 | 5.1770 | 3.9811 | 2.9811 | 35.3503 |

## SVoI: vehicles decided after k observations

| observations used | H=1 | H=2 | H=3 | H=5 |
|---|---|---|---|---|
| 1 | 83232 | 83232 | 81331 | 81331 |
| 2 | 40388 | 26556 | 27912 | 20101 |
| 3 | 0 | 13832 | 4998 | 6832 |
| 4 | 0 | 0 | 9379 | 7226 |
| 5 | 0 | 0 | 0 | 2611 |
| 6 | 0 | 0 | 0 | 5519 |
