# ADDR: stealthy targeted poisoning (row 18)

RAVEN-X-GF, 20 RSUs (spatial), one compromised RSU. 10 honest rounds, then 3 rounds with the attacker active. Boost 20; target messages ≈ 20% of the attacker's local training stream. Decisions at the steps where the honest SVoI controller (H = 3) stops; Eq. 14 decision on each model's own validation-calibrated belief. 'future' = the half of the target's messages the attacker never saw; 'seen' = the half it trained on (upper bound). 'honest (rerun)' is a second honest continuation: its ADDR is the noise floor.

## Summary (mean over targets, worst case = highest)

Targets on which the honest controller made no decision in the future half are left out of the means ('n targets').

| Aggregator | Model | Targets | n targets | ADDR future, mean | ADDR future, worst | wrongly accepted (future) | wrongly rejected (future) | ADDR seen, mean | ADDR seen, worst | val F1 | val F1 (honest) | val ECE | val ECE (honest) | ‖Δθ‖ / round update |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FedAvg | honest (rerun) | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8575 | 0.8575 | 0.0221 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8575 | 0.8575 | 0.0221 | 0.0221 | 0.0000 |
| FedAvg | norm-matched | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0421 | 0.2105 | 0.8431 | 0.8575 | 0.0254 | 0.0221 | 1.4003 |
| FedAvg | boosted | attacker | 5 | 0.3560 | 0.8293 | 0.3116 | 0.0444 | 0.5140 | 1.0000 | 0.5217 | 0.8575 | 0.1079 | 0.0221 | 18.1746 |
| FedAvg | norm-matched | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8367 | 0.8575 | 0.0292 | 0.0221 | 1.4510 |
| FedAvg | boosted | honest | 5 | 0.6008 | 1.0000 | 0.0000 | 0.6008 | 0.6770 | 1.0000 | 0.4210 | 0.8575 | 0.1502 | 0.0221 | 19.0198 |
| RS-WeightedTrim | honest (rerun) | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8357 | 0.8353 | 0.0349 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8357 | 0.8353 | 0.0349 | 0.0349 | 0.0000 |
| RS-WeightedTrim | norm-matched | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8346 | 0.8353 | 0.0358 | 0.0349 | 0.9540 |
| RS-WeightedTrim | boosted | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8361 | 0.8353 | 0.0354 | 0.0349 | 1.1102 |
| RS-WeightedTrim | norm-matched | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8407 | 0.8353 | 0.0345 | 0.0349 | 0.9626 |
| RS-WeightedTrim | boosted | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8321 | 0.8353 | 0.0362 | 0.0349 | 1.1334 |

## Per target

| Aggregator | Model | Target | Honest decides (%) | Honest rejects (% of decisions) | ADDR (future) | wrongly accepted (future) | wrongly rejected (future) | decisions (future) | ADDR (seen) | val F1 | val ECE | ‖Δθ‖ / round update |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FedAvg | honest (rerun) | attacker:positionMirroring:2530385657 | 54.7009 | 26.5625 | 0.0000 | 0.0000 | 0.0000 | 45 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | attacker:randomPositionOffset:5274206664 | 94.9367 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | attacker:randomSpeedOffset:7761870589 | 93.9655 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 108 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | attacker:dataReplay:4623714049 | 74.3590 | 96.5517 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | honest:zeroSpeedReport:9129455203 | 49.6503 | 2.8169 | 0.0000 | 0.0000 | 0.0000 | 102 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | honest:feignedBraking:4434209032 | 23.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 14 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | honest:trafficCongestionSybil:7802626606 | 88.8889 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 45 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | honest:dataReplay:5628007782 | 40.0000 | 21.8750 | 0.0000 | 0.0000 | 0.0000 | 34 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | honest (rerun) | honest:randomSpeedOffset:5142823020 | 59.8214 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 34 | 0.0000 | 0.8575 | 0.0221 | 0.0000 |
| FedAvg | norm-matched | attacker:positionMirroring:2530385657 | 54.7009 | 26.5625 | 0.0000 | 0.0000 | 0.0000 | 45 | 0.2105 | 0.8413 | 0.0243 | 1.1770 |
| FedAvg | boosted | attacker:positionMirroring:2530385657 | 54.7009 | 26.5625 | 0.2444 | 0.0222 | 0.2222 | 45 | 0.0000 | 0.4958 | 0.1222 | 16.3007 |
| FedAvg | norm-matched | attacker:randomPositionOffset:5274206664 | 94.9367 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8461 | 0.0247 | 1.4980 |
| FedAvg | boosted | attacker:randomPositionOffset:5274206664 | 94.9367 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.5000 | 0.5885 | 0.0724 | 19.5230 |
| FedAvg | norm-matched | attacker:randomSpeedOffset:7761870589 | 93.9655 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 108 | 0.0000 | 0.8468 | 0.0257 | 1.5379 |
| FedAvg | boosted | attacker:randomSpeedOffset:7761870589 | 93.9655 | 100.0000 | 0.4352 | 0.4352 | 0.0000 | 108 | 0.9273 | 0.5221 | 0.1132 | 19.6579 |
| FedAvg | norm-matched | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8437 | 0.0254 | 1.4506 |
| FedAvg | boosted | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.8293 | 0.8293 | 0.0000 | 41 | 1.0000 | 0.5378 | 0.0790 | 18.1115 |
| FedAvg | norm-matched | attacker:dataReplay:4623714049 | 74.3590 | 96.5517 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8378 | 0.0267 | 1.3383 |
| FedAvg | boosted | attacker:dataReplay:4623714049 | 74.3590 | 96.5517 | 0.2712 | 0.2712 | 0.0000 | 59 | 0.1429 | 0.4646 | 0.1527 | 17.2800 |
| FedAvg | norm-matched | honest:zeroSpeedReport:9129455203 | 49.6503 | 2.8169 | 0.0000 | 0.0000 | 0.0000 | 102 | 0.0000 | 0.8225 | 0.0328 | 1.5298 |
| FedAvg | boosted | honest:zeroSpeedReport:9129455203 | 49.6503 | 2.8169 | 1.0000 | 0.0000 | 1.0000 | 102 | 0.9000 | 0.3353 | 0.1987 | 20.3678 |
| FedAvg | norm-matched | honest:feignedBraking:4434209032 | 23.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 14 | 0.0000 | 0.8398 | 0.0289 | 1.3965 |
| FedAvg | boosted | honest:feignedBraking:4434209032 | 23.3333 | 0.0000 | 0.3571 | 0.0000 | 0.3571 | 14 | 0.0000 | 0.4408 | 0.1356 | 17.1690 |
| FedAvg | norm-matched | honest:trafficCongestionSybil:7802626606 | 88.8889 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 45 | 0.0000 | 0.8284 | 0.0315 | 1.4750 |
| FedAvg | boosted | honest:trafficCongestionSybil:7802626606 | 88.8889 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 45 | 1.0000 | 0.3353 | 0.1868 | 18.4962 |
| FedAvg | norm-matched | honest:dataReplay:5628007782 | 40.0000 | 21.8750 | 0.0000 | 0.0000 | 0.0000 | 34 | 0.0000 | 0.8447 | 0.0251 | 1.3411 |
| FedAvg | boosted | honest:dataReplay:5628007782 | 40.0000 | 21.8750 | 0.5882 | 0.0000 | 0.5882 | 34 | 1.0000 | 0.3403 | 0.1949 | 17.8993 |
| FedAvg | norm-matched | honest:randomSpeedOffset:5142823020 | 59.8214 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 34 | 0.0000 | 0.8483 | 0.0276 | 1.5124 |
| FedAvg | boosted | honest:randomSpeedOffset:5142823020 | 59.8214 | 0.0000 | 0.0588 | 0.0000 | 0.0588 | 34 | 0.4848 | 0.6532 | 0.0352 | 21.1670 |
| RS-WeightedTrim | honest (rerun) | attacker:positionMirroring:2530385657 | 35.8974 | 76.1905 | 0.0000 | 0.0000 | 0.0000 | 25 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:randomPositionOffset:5274206664 | 94.9367 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:randomSpeedOffset:7761870589 | 96.1207 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 111 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:dataReplay:4623714049 | 79.4872 | 95.6989 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:zeroSpeedReport:9129455203 | 52.4476 | 14.0000 | 0.0000 | 0.0000 | 0.0000 | 112 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:feignedBraking:4434209032 | 23.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 14 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:trafficCongestionSybil:7802626606 | 77.7778 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 40 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:dataReplay:5628007782 | 23.1250 | 48.6486 | 0.0000 | 0.0000 | 0.0000 | 20 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:randomSpeedOffset:5142823020 | 53.5714 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 28 | 0.0000 | 0.8357 | 0.0349 | 0.0000 |
| RS-WeightedTrim | norm-matched | attacker:positionMirroring:2530385657 | 35.8974 | 76.1905 | 0.0000 | 0.0000 | 0.0000 | 25 | 0.0000 | 0.8427 | 0.0337 | 0.8847 |
| RS-WeightedTrim | boosted | attacker:positionMirroring:2530385657 | 35.8974 | 76.1905 | 0.0000 | 0.0000 | 0.0000 | 25 | 0.0000 | 0.8481 | 0.0320 | 1.0615 |
| RS-WeightedTrim | norm-matched | attacker:randomPositionOffset:5274206664 | 94.9367 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8274 | 0.0387 | 0.9988 |
| RS-WeightedTrim | boosted | attacker:randomPositionOffset:5274206664 | 94.9367 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8432 | 0.0335 | 1.1384 |
| RS-WeightedTrim | norm-matched | attacker:randomSpeedOffset:7761870589 | 96.1207 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 111 | 0.0000 | 0.8287 | 0.0370 | 1.0083 |
| RS-WeightedTrim | boosted | attacker:randomSpeedOffset:7761870589 | 96.1207 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 111 | 0.0000 | 0.8236 | 0.0388 | 1.1455 |
| RS-WeightedTrim | norm-matched | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8357 | 0.0362 | 0.9638 |
| RS-WeightedTrim | boosted | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8321 | 0.0370 | 1.1203 |
| RS-WeightedTrim | norm-matched | attacker:dataReplay:4623714049 | 79.4872 | 95.6989 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8385 | 0.0334 | 0.9145 |
| RS-WeightedTrim | boosted | attacker:dataReplay:4623714049 | 79.4872 | 95.6989 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8335 | 0.0356 | 1.0854 |
| RS-WeightedTrim | norm-matched | honest:zeroSpeedReport:9129455203 | 52.4476 | 14.0000 | 0.0000 | 0.0000 | 0.0000 | 112 | 0.0000 | 0.8352 | 0.0357 | 0.9911 |
| RS-WeightedTrim | boosted | honest:zeroSpeedReport:9129455203 | 52.4476 | 14.0000 | 0.0000 | 0.0000 | 0.0000 | 112 | 0.0000 | 0.8379 | 0.0343 | 1.1400 |
| RS-WeightedTrim | norm-matched | honest:feignedBraking:4434209032 | 23.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 14 | 0.0000 | 0.8484 | 0.0321 | 0.9401 |
| RS-WeightedTrim | boosted | honest:feignedBraking:4434209032 | 23.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 14 | 0.0000 | 0.8355 | 0.0351 | 1.1170 |
| RS-WeightedTrim | norm-matched | honest:trafficCongestionSybil:7802626606 | 77.7778 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 40 | 0.0000 | 0.8417 | 0.0345 | 0.9727 |
| RS-WeightedTrim | boosted | honest:trafficCongestionSybil:7802626606 | 77.7778 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 40 | 0.0000 | 0.8277 | 0.0376 | 1.1461 |
| RS-WeightedTrim | norm-matched | honest:dataReplay:5628007782 | 23.1250 | 48.6486 | 0.0000 | 0.0000 | 0.0000 | 20 | 0.0000 | 0.8446 | 0.0331 | 0.9355 |
| RS-WeightedTrim | boosted | honest:dataReplay:5628007782 | 23.1250 | 48.6486 | 0.0000 | 0.0000 | 0.0000 | 20 | 0.0000 | 0.8254 | 0.0381 | 1.1281 |
| RS-WeightedTrim | norm-matched | honest:randomSpeedOffset:5142823020 | 53.5714 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 28 | 0.0000 | 0.8335 | 0.0371 | 0.9737 |
| RS-WeightedTrim | boosted | honest:randomSpeedOffset:5142823020 | 53.5714 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 28 | 0.0000 | 0.8342 | 0.0360 | 1.1356 |
## Reading the results (19-feature RAVEN-X-GF)

- **The noise floor is exactly zero.** Both honest reruns reproduce the
  honest model bit for bit, so every flip below comes from the attacker.
- **RS-WeightedTrim: no flips at all.** 0 of 10 targets, on unseen and on
  seen messages alike, at both strengths. Validation F1 stays at
  0.824–0.848 against 0.835 for the honest model, and ECE is unchanged.
- **FedAvg, norm-matched: no flips on future decisions.** On the messages
  the attacker trained on, it flips 21% for one target (Position
  Mirroring). That attack is a little less stealthy than in the 17-feature
  run: validation F1 falls 0.009–0.034 (0.857 → 0.823–0.848).
- **FedAvg, boosted: it flips, but it isn't stealthy.** Mean ADDR on unseen
  messages is 0.36 for attacker targets (mostly wrongly accepted; worst
  case 0.83, the DoS vehicle) and 0.60 for honest targets (all wrongly
  rejected; worst case 1.0). Validation F1 collapses from 0.857 to
  0.34–0.65 and the model moves about 18 rounds' worth, which a server
  watching validation metrics would catch.
- The overall picture matches the 17-feature run. The defence holds
  against this attacker, and the only working attack (boosted, under
  FedAvg) is loud. The caveat still applies: this is one fixed attack
  recipe, not an adaptive attacker.
