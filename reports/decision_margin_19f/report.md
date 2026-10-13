# How much model change flips decisions (row 19)

Honest federated RAVEN-X-GF from `results/addr_nbr`; decisions compared at the steps of a 20,000-step test sample where the honest SVoI controller (H = 3) stops. Temperature fixed at the honest model's. Scale = ‖Δθ‖ in multiples of the median honest round update norm.

## Flip rate by direction family

| Aggregator | Family | Scale (rounds) | flip rate, mean | flip rate, worst | wrongly accepted mean | wrongly accepted max | wrongly rejected mean | wrongly rejected max |
|---|---|---|---|---|---|---|---|---|
| FedAvg | attack boosted | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack boosted | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack boosted | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack boosted | 3.0000 | 0.0004 | 0.0030 | 0.0001 | 0.0003 | 0.0004 | 0.0030 |
| FedAvg | attack boosted | 10.0000 | 0.0497 | 0.1194 | 0.0054 | 0.0110 | 0.0442 | 0.1183 |
| FedAvg | attack boosted | 30.0000 | 0.3545 | 0.5932 | 0.0352 | 0.1432 | 0.3193 | 0.5865 |
| FedAvg | attack norm-matched | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack norm-matched | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack norm-matched | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack norm-matched | 3.0000 | 0.0005 | 0.0022 | 0.0001 | 0.0003 | 0.0004 | 0.0019 |
| FedAvg | attack norm-matched | 10.0000 | 0.0620 | 0.1705 | 0.0044 | 0.0081 | 0.0576 | 0.1680 |
| FedAvg | attack norm-matched | 30.0000 | 0.4579 | 0.6821 | 0.0185 | 0.0409 | 0.4394 | 0.6756 |
| FedAvg | gradient | 0.1000 | 0.0033 | 0.0033 | 0.0000 | 0.0000 | 0.0033 | 0.0033 |
| FedAvg | gradient | 0.3000 | 0.3930 | 0.3930 | 0.0002 | 0.0002 | 0.3928 | 0.3928 |
| FedAvg | gradient | 1.0000 | 0.7143 | 0.7143 | 0.0071 | 0.0071 | 0.7072 | 0.7072 |
| FedAvg | gradient | 3.0000 | 0.7564 | 0.7564 | 0.0339 | 0.0339 | 0.7225 | 0.7225 |
| FedAvg | gradient | 10.0000 | 0.8017 | 0.8017 | 0.0726 | 0.0726 | 0.7291 | 0.7291 |
| FedAvg | gradient | 30.0000 | 0.4241 | 0.4241 | 0.1383 | 0.1383 | 0.2858 | 0.2858 |
| FedAvg | random | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 10.0000 | 0.0158 | 0.0520 | 0.0020 | 0.0049 | 0.0138 | 0.0471 |
| FedAvg | random | 30.0000 | 0.1837 | 0.3025 | 0.0249 | 0.0315 | 0.1588 | 0.2813 |
| FedAvg | reverse | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | reverse | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | reverse | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | reverse | 3.0000 | 0.0001 | 0.0001 | 0.0001 | 0.0001 | 0.0000 | 0.0000 |
| FedAvg | reverse | 10.0000 | 0.0160 | 0.0160 | 0.0038 | 0.0038 | 0.0122 | 0.0122 |
| FedAvg | reverse | 30.0000 | 0.7291 | 0.7291 | 0.0000 | 0.0000 | 0.7291 | 0.7291 |
| RS-WeightedTrim | attack boosted | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 1.0000 | 0.0000 | 0.0002 | 0.0000 | 0.0002 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 3.0000 | 0.0012 | 0.0064 | 0.0011 | 0.0064 | 0.0001 | 0.0009 |
| RS-WeightedTrim | attack boosted | 10.0000 | 0.0601 | 0.1135 | 0.0107 | 0.0197 | 0.0493 | 0.1060 |
| RS-WeightedTrim | attack boosted | 30.0000 | 0.4629 | 0.5944 | 0.0194 | 0.0348 | 0.4435 | 0.5750 |
| RS-WeightedTrim | attack norm-matched | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack norm-matched | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack norm-matched | 1.0000 | 0.0000 | 0.0001 | 0.0000 | 0.0001 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack norm-matched | 3.0000 | 0.0021 | 0.0073 | 0.0020 | 0.0073 | 0.0001 | 0.0008 |
| RS-WeightedTrim | attack norm-matched | 10.0000 | 0.0524 | 0.1012 | 0.0128 | 0.0208 | 0.0396 | 0.0991 |
| RS-WeightedTrim | attack norm-matched | 30.0000 | 0.3878 | 0.5377 | 0.0272 | 0.0589 | 0.3607 | 0.5278 |
| RS-WeightedTrim | gradient | 0.1000 | 0.0004 | 0.0004 | 0.0004 | 0.0004 | 0.0000 | 0.0000 |
| RS-WeightedTrim | gradient | 0.3000 | 0.1299 | 0.1299 | 0.0100 | 0.0100 | 0.1199 | 0.1199 |
| RS-WeightedTrim | gradient | 1.0000 | 0.6689 | 0.6689 | 0.0134 | 0.0134 | 0.6554 | 0.6554 |
| RS-WeightedTrim | gradient | 3.0000 | 0.7112 | 0.7112 | 0.0373 | 0.0373 | 0.6739 | 0.6739 |
| RS-WeightedTrim | gradient | 10.0000 | 0.6855 | 0.6855 | 0.0000 | 0.0000 | 0.6855 | 0.6855 |
| RS-WeightedTrim | gradient | 30.0000 | 0.4760 | 0.4760 | 0.0471 | 0.0471 | 0.4289 | 0.4289 |
| RS-WeightedTrim | random | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 3.0000 | 0.0002 | 0.0006 | 0.0002 | 0.0006 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 10.0000 | 0.0120 | 0.0253 | 0.0081 | 0.0164 | 0.0039 | 0.0137 |
| RS-WeightedTrim | random | 30.0000 | 0.2107 | 0.3524 | 0.0412 | 0.0622 | 0.1694 | 0.3418 |
| RS-WeightedTrim | reverse | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 3.0000 | 0.0008 | 0.0008 | 0.0008 | 0.0008 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 10.0000 | 0.0120 | 0.0120 | 0.0080 | 0.0080 | 0.0040 | 0.0040 |
| RS-WeightedTrim | reverse | 30.0000 | 0.6855 | 0.6855 | 0.0000 | 0.0000 | 0.6855 | 0.6855 |

## Row 18 deviations on the same scale (dotted lines in the plots)

| Aggregator | Row-18 model | ‖Δθ‖ / round update, mean | ‖Δθ‖ / round update, max |
|---|---|---|---|
| RS-WeightedTrim | boosted | 1.1218 | 1.1461 |
| RS-WeightedTrim | honest (rerun) | 0.0000 | 0.0000 |
| RS-WeightedTrim | norm-matched | 0.9583 | 1.0083 |
| FedAvg | boosted | 18.5972 | 21.1670 |
| FedAvg | honest (rerun) | 0.0000 | 0.0000 |
| FedAvg | norm-matched | 1.4257 | 1.5379 |
## Reading the results (19-feature RAVEN-X-GF)

- **Along random, reverse and row-18 attack directions,** at most 0.2% of
  decisions flip up to 3 rounds' worth of change. At 10 rounds, 1–6% flip.
- **Along the gradient (first-order worst case),** 13% (RS-WeightedTrim)
  and 39% (FedAvg) flip at 0.3 rounds' worth, and 67–71% at 1 round's
  worth. Almost all of these are wrongly rejected.
- **Row 18's attacks under RS-WeightedTrim** moved the model 0.96–1.12
  rounds' worth. Along their own directions that flips nothing, which
  matches their ADDR of 0. Along the gradient direction, the same size
  would flip about two-thirds of decisions. The safety margin depends on
  direction, as in the 17-feature run; a formal guarantee needs Theorem 1's
  constants.
