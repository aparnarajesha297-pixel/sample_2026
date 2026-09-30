# How much model change flips decisions (row 19)

Honest federated RAVEN-X-GF from `results/addr`; decisions compared at the steps of a 20,000-step test sample where the honest SVoI controller (H = 3) stops. Temperature fixed at the honest model's. Scale = ‖Δθ‖ in multiples of the median honest round update norm.

## Flip rate by direction family

| Aggregator | Family | Scale (rounds) | flip rate, mean | flip rate, worst | wrongly accepted mean | wrongly accepted max | wrongly rejected mean | wrongly rejected max |
|---|---|---|---|---|---|---|---|---|
| FedAvg | attack boosted | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack boosted | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack boosted | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack boosted | 3.0000 | 0.0009 | 0.0034 | 0.0006 | 0.0033 | 0.0003 | 0.0016 |
| FedAvg | attack boosted | 10.0000 | 0.0463 | 0.1559 | 0.0096 | 0.0305 | 0.0367 | 0.1254 |
| FedAvg | attack boosted | 30.0000 | 0.3662 | 0.5381 | 0.0353 | 0.1101 | 0.3309 | 0.5319 |
| FedAvg | attack norm-matched | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack norm-matched | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | attack norm-matched | 1.0000 | 0.0000 | 0.0002 | 0.0000 | 0.0002 | 0.0000 | 0.0000 |
| FedAvg | attack norm-matched | 3.0000 | 0.0009 | 0.0024 | 0.0006 | 0.0014 | 0.0003 | 0.0011 |
| FedAvg | attack norm-matched | 10.0000 | 0.0599 | 0.0951 | 0.0137 | 0.0314 | 0.0462 | 0.0874 |
| FedAvg | attack norm-matched | 30.0000 | 0.4134 | 0.5686 | 0.0812 | 0.1662 | 0.3323 | 0.5310 |
| FedAvg | gradient | 0.1000 | 0.0033 | 0.0033 | 0.0000 | 0.0000 | 0.0033 | 0.0033 |
| FedAvg | gradient | 0.3000 | 0.3257 | 0.3257 | 0.0001 | 0.0001 | 0.3256 | 0.3256 |
| FedAvg | gradient | 1.0000 | 0.6560 | 0.6560 | 0.0199 | 0.0199 | 0.6361 | 0.6361 |
| FedAvg | gradient | 3.0000 | 0.7298 | 0.7298 | 0.0783 | 0.0783 | 0.6516 | 0.6516 |
| FedAvg | gradient | 10.0000 | 0.6554 | 0.6554 | 0.0000 | 0.0000 | 0.6554 | 0.6554 |
| FedAvg | gradient | 30.0000 | 0.3788 | 0.3788 | 0.2330 | 0.2330 | 0.1458 | 0.1458 |
| FedAvg | random | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | random | 10.0000 | 0.0106 | 0.0162 | 0.0031 | 0.0056 | 0.0075 | 0.0134 |
| FedAvg | random | 30.0000 | 0.2366 | 0.3391 | 0.0501 | 0.0854 | 0.1865 | 0.2873 |
| FedAvg | reverse | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | reverse | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | reverse | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| FedAvg | reverse | 3.0000 | 0.0001 | 0.0001 | 0.0001 | 0.0001 | 0.0000 | 0.0000 |
| FedAvg | reverse | 10.0000 | 0.0139 | 0.0139 | 0.0071 | 0.0071 | 0.0067 | 0.0067 |
| FedAvg | reverse | 30.0000 | 0.6554 | 0.6554 | 0.0000 | 0.0000 | 0.6554 | 0.6554 |
| RS-WeightedTrim | attack boosted | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 3.0000 | 0.0001 | 0.0002 | 0.0001 | 0.0002 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack boosted | 10.0000 | 0.0162 | 0.0447 | 0.0029 | 0.0043 | 0.0133 | 0.0424 |
| RS-WeightedTrim | attack boosted | 30.0000 | 0.3306 | 0.5643 | 0.0224 | 0.0462 | 0.3082 | 0.5619 |
| RS-WeightedTrim | attack norm-matched | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack norm-matched | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack norm-matched | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | attack norm-matched | 3.0000 | 0.0001 | 0.0003 | 0.0001 | 0.0003 | 0.0000 | 0.0001 |
| RS-WeightedTrim | attack norm-matched | 10.0000 | 0.0241 | 0.0527 | 0.0042 | 0.0146 | 0.0199 | 0.0518 |
| RS-WeightedTrim | attack norm-matched | 30.0000 | 0.4572 | 0.6797 | 0.0194 | 0.0616 | 0.4377 | 0.6797 |
| RS-WeightedTrim | gradient | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | gradient | 0.3000 | 0.0540 | 0.0540 | 0.0000 | 0.0000 | 0.0540 | 0.0540 |
| RS-WeightedTrim | gradient | 1.0000 | 0.6461 | 0.6461 | 0.0009 | 0.0009 | 0.6452 | 0.6452 |
| RS-WeightedTrim | gradient | 3.0000 | 0.7290 | 0.7290 | 0.0480 | 0.0480 | 0.6811 | 0.6811 |
| RS-WeightedTrim | gradient | 10.0000 | 0.6823 | 0.6823 | 0.0000 | 0.0000 | 0.6823 | 0.6823 |
| RS-WeightedTrim | gradient | 30.0000 | 0.3210 | 0.3210 | 0.0512 | 0.0512 | 0.2698 | 0.2698 |
| RS-WeightedTrim | random | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | random | 10.0000 | 0.0015 | 0.0033 | 0.0008 | 0.0016 | 0.0007 | 0.0027 |
| RS-WeightedTrim | random | 30.0000 | 0.1040 | 0.1277 | 0.0231 | 0.0498 | 0.0809 | 0.1085 |
| RS-WeightedTrim | reverse | 0.1000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 0.3000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 3.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| RS-WeightedTrim | reverse | 10.0000 | 0.0029 | 0.0029 | 0.0018 | 0.0018 | 0.0011 | 0.0011 |
| RS-WeightedTrim | reverse | 30.0000 | 0.6823 | 0.6823 | 0.0000 | 0.0000 | 0.6823 | 0.6823 |

## Row 18 deviations on the same scale (dotted lines in the plots)

| Aggregator | Row-18 model | ‖Δθ‖ / round update, mean | ‖Δθ‖ / round update, max |
|---|---|---|---|
| RS-WeightedTrim | boosted | 1.0918 | 1.1273 |
| RS-WeightedTrim | honest (rerun) | 0.0000 | 0.0000 |
| RS-WeightedTrim | norm-matched | 0.9201 | 0.9658 |
| FedAvg | boosted | 17.9992 | 20.5214 |
| FedAvg | honest (rerun) | 0.0000 | 0.0000 |
| FedAvg | norm-matched | 1.4003 | 1.5328 |
## Reading the results

- **The margin depends on the direction.** Along random, reversed-training
  and row-18 attack directions, no decisions flip up to 3 rounds' worth of
  change: at most 0.1%. At 10 rounds' worth, 0.2–6% flip. At 30 rounds'
  worth, 10–68% flip.
- **The first-order worst case is much closer.** Along the gradient
  direction, 5% (RS-WeightedTrim) and 33% (FedAvg) of decisions flip at 0.3
  rounds' worth, and about 65% at 1 round's worth. Nearly all of these are
  wrongly rejected: the easiest way to flip decisions is to push everything
  towards "reject". The curve falls again at large steps because a
  linearised direction stops working far from the model.
- **Where row 18 sits.** Row 18's attacks under RS-WeightedTrim moved the
  model 0.9–1.1 rounds' worth, and along their own directions that flips
  essentially nothing, which matches their ADDR of 0. A deviation of the
  same size along the gradient direction would flip about 65% of decisions.
  So the safety of RS-WeightedTrim in row 18 comes from the attacker not
  finding that direction, not from the deviation bound alone. Whether a
  single RSU *can* steer the trimmed mean along the gradient direction is
  exactly what Theorem 1's bound, together with the trimming, should limit.
  That needs the theorem's constants to check.
- **One caveat:** the gradient direction flips decisions *globally*. It
  would also wreck validation F1, so it isn't a stealthy targeted attack. It
  gives the geometric worst case, not an achievable one.
