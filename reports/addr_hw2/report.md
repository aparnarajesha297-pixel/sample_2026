# ADDR: stealthy targeted poisoning (row 18)

RAVEN-X-GF, 20 RSUs (spatial), one compromised RSU. 10 honest rounds, then 3 rounds with the attacker active. Boost 20; target messages ≈ 20% of the attacker's local training stream. Decisions at the steps where the honest SVoI controller (H = 3) stops; Eq. 14 decision on each model's own validation-calibrated belief. 'future' = the half of the target's messages the attacker never saw; 'seen' = the half it trained on (upper bound). 'honest (rerun)' is a second honest continuation: its ADDR is the noise floor.

## Summary (mean over targets, worst case = highest)

Targets on which the honest controller made no decision in the future half are left out of the means ('n targets').

| Aggregator | Model | Targets | n targets | ADDR future, mean | ADDR future, worst | wrongly accepted (future) | wrongly rejected (future) | ADDR seen, mean | ADDR seen, worst | val F1 | val F1 (honest) | val ECE | val ECE (honest) | ‖Δθ‖ / round update |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FedAvg | honest (rerun) | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8533 | 0.8516 | 0.0267 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | honest | 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8533 | 0.8516 | 0.0267 | 0.0267 | 0.0000 |
| FedAvg | norm-matched | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8527 | 0.8516 | 0.0264 | 0.0267 | 1.3798 |
| FedAvg | boosted | attacker | 5 | 0.3304 | 0.9487 | 0.3227 | 0.0077 | 0.7710 | 1.0000 | 0.5276 | 0.8516 | 0.1346 | 0.0267 | 17.4927 |
| FedAvg | norm-matched | honest | 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8518 | 0.8516 | 0.0273 | 0.0267 | 1.4404 |
| FedAvg | boosted | honest | 4 | 0.7808 | 1.0000 | 0.0000 | 0.7808 | 0.7798 | 1.0000 | 0.4066 | 0.8516 | 0.1756 | 0.0267 | 18.6713 |
| RS-WeightedTrim | honest (rerun) | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8346 | 0.8325 | 0.0363 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8346 | 0.8325 | 0.0363 | 0.0363 | 0.0000 |
| RS-WeightedTrim | norm-matched | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8352 | 0.8325 | 0.0361 | 0.0363 | 0.9156 |
| RS-WeightedTrim | boosted | attacker | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8313 | 0.8325 | 0.0371 | 0.0363 | 1.0812 |
| RS-WeightedTrim | norm-matched | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8334 | 0.8325 | 0.0374 | 0.0363 | 0.9246 |
| RS-WeightedTrim | boosted | honest | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8322 | 0.8325 | 0.0372 | 0.0363 | 1.1025 |

## Per target

| Aggregator | Model | Target | Honest decides (%) | Honest rejects (% of decisions) | ADDR (future) | wrongly accepted (future) | wrongly rejected (future) | decisions (future) | ADDR (seen) | val F1 | val ECE | ‖Δθ‖ / round update |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FedAvg | honest (rerun) | attacker:positionMirroring:2530385657 | 35.8974 | 38.0952 | 0.0000 | 0.0000 | 0.0000 | 26 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | attacker:randomPositionOffset:5274206664 | 93.6709 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | attacker:randomSpeedOffset:7761870589 | 94.3966 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 109 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | attacker:dataReplay:4623714049 | 74.3590 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | honest:zeroSpeedReport:9129455203 | 37.0629 | 14.1509 | 0.0000 | 0.0000 | 0.0000 | 75 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | honest:feignedBraking:4434209032 | 0.0000 | nan | 0.0000 | 0.0000 | 0.0000 | 0 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | honest:trafficCongestionSybil:7802626606 | 70.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 29 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | honest:dataReplay:5628007782 | 20.6250 | 60.6061 | 0.0000 | 0.0000 | 0.0000 | 20 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | honest (rerun) | honest:randomSpeedOffset:5142823020 | 49.1071 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 25 | 0.0000 | 0.8533 | 0.0267 | 0.0000 |
| FedAvg | norm-matched | attacker:positionMirroring:2530385657 | 35.8974 | 38.0952 | 0.0000 | 0.0000 | 0.0000 | 26 | 0.0000 | 0.8472 | 0.0294 | 1.1846 |
| FedAvg | boosted | attacker:positionMirroring:2530385657 | 35.8974 | 38.0952 | 0.0385 | 0.0000 | 0.0385 | 26 | 0.5625 | 0.7015 | 0.0510 | 15.2349 |
| FedAvg | norm-matched | attacker:randomPositionOffset:5274206664 | 93.6709 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8438 | 0.0283 | 1.4384 |
| FedAvg | boosted | attacker:randomPositionOffset:5274206664 | 93.6709 | 100.0000 | 0.9487 | 0.9487 | 0.0000 | 39 | 1.0000 | 0.3258 | 0.3054 | 18.7986 |
| FedAvg | norm-matched | attacker:randomSpeedOffset:7761870589 | 94.3966 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 109 | 0.0000 | 0.8565 | 0.0253 | 1.5064 |
| FedAvg | boosted | attacker:randomSpeedOffset:7761870589 | 94.3966 | 100.0000 | 0.4954 | 0.4954 | 0.0000 | 109 | 0.9909 | 0.5141 | 0.1117 | 18.8108 |
| FedAvg | norm-matched | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8600 | 0.0231 | 1.4028 |
| FedAvg | boosted | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.6585 | 0.6312 | 0.0647 | 17.5833 |
| FedAvg | norm-matched | attacker:dataReplay:4623714049 | 74.3590 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8559 | 0.0261 | 1.3667 |
| FedAvg | boosted | attacker:dataReplay:4623714049 | 74.3590 | 100.0000 | 0.1695 | 0.1695 | 0.0000 | 59 | 0.6429 | 0.4655 | 0.1400 | 17.0358 |
| FedAvg | norm-matched | honest:zeroSpeedReport:9129455203 | 37.0629 | 14.1509 | 0.0000 | 0.0000 | 0.0000 | 75 | 0.0000 | 0.8492 | 0.0292 | 1.5328 |
| FedAvg | boosted | honest:zeroSpeedReport:9129455203 | 37.0629 | 14.1509 | 0.9733 | 0.0000 | 0.9733 | 75 | 0.5806 | 0.3353 | 0.2617 | 20.5214 |
| FedAvg | norm-matched | honest:feignedBraking:4434209032 | 0.0000 | nan | 0.0000 | 0.0000 | 0.0000 | 0 | 0.0000 | 0.8478 | 0.0287 | 1.3426 |
| FedAvg | boosted | honest:feignedBraking:4434209032 | 0.0000 | nan | 0.0000 | 0.0000 | 0.0000 | 0 | 0.0000 | 0.3380 | 0.1618 | 17.8430 |
| FedAvg | norm-matched | honest:trafficCongestionSybil:7802626606 | 70.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 29 | 0.0000 | 0.8570 | 0.0245 | 1.4234 |
| FedAvg | boosted | honest:trafficCongestionSybil:7802626606 | 70.0000 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 29 | 1.0000 | 0.3419 | 0.1792 | 17.7781 |
| FedAvg | norm-matched | honest:dataReplay:5628007782 | 20.6250 | 60.6061 | 0.0000 | 0.0000 | 0.0000 | 20 | 0.0000 | 0.8467 | 0.0291 | 1.3093 |
| FedAvg | boosted | honest:dataReplay:5628007782 | 20.6250 | 60.6061 | 0.1500 | 0.0000 | 0.1500 | 20 | 0.5385 | 0.6089 | 0.0704 | 16.2139 |
| FedAvg | norm-matched | honest:randomSpeedOffset:5142823020 | 49.1071 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 25 | 0.0000 | 0.8544 | 0.0264 | 1.4962 |
| FedAvg | boosted | honest:randomSpeedOffset:5142823020 | 49.1071 | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 25 | 1.0000 | 0.3405 | 0.1914 | 20.1718 |
| RS-WeightedTrim | honest (rerun) | attacker:positionMirroring:2530385657 | 20.5128 | 50.0000 | 0.0000 | 0.0000 | 0.0000 | 23 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:randomPositionOffset:5274206664 | 93.6709 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:randomSpeedOffset:7761870589 | 94.3966 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 109 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | attacker:dataReplay:4623714049 | 71.7949 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:zeroSpeedReport:9129455203 | 44.0559 | 2.3810 | 0.0000 | 0.0000 | 0.0000 | 113 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:feignedBraking:4434209032 | 3.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:trafficCongestionSybil:7802626606 | 78.8889 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 36 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:dataReplay:5628007782 | 21.2500 | 76.4706 | 0.0000 | 0.0000 | 0.0000 | 23 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | honest (rerun) | honest:randomSpeedOffset:5142823020 | 61.6071 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 28 | 0.0000 | 0.8346 | 0.0363 | 0.0000 |
| RS-WeightedTrim | norm-matched | attacker:positionMirroring:2530385657 | 20.5128 | 50.0000 | 0.0000 | 0.0000 | 0.0000 | 23 | 0.0000 | 0.8301 | 0.0368 | 0.8319 |
| RS-WeightedTrim | boosted | attacker:positionMirroring:2530385657 | 20.5128 | 50.0000 | 0.0000 | 0.0000 | 0.0000 | 23 | 0.0000 | 0.8382 | 0.0355 | 1.0219 |
| RS-WeightedTrim | norm-matched | attacker:randomPositionOffset:5274206664 | 93.6709 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8304 | 0.0374 | 0.9334 |
| RS-WeightedTrim | boosted | attacker:randomPositionOffset:5274206664 | 93.6709 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 39 | 0.0000 | 0.8275 | 0.0387 | 1.0845 |
| RS-WeightedTrim | norm-matched | attacker:randomSpeedOffset:7761870589 | 94.3966 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 109 | 0.0000 | 0.8351 | 0.0368 | 0.9658 |
| RS-WeightedTrim | boosted | attacker:randomSpeedOffset:7761870589 | 94.3966 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 109 | 0.0000 | 0.8298 | 0.0373 | 1.1089 |
| RS-WeightedTrim | norm-matched | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8397 | 0.0346 | 0.9399 |
| RS-WeightedTrim | boosted | attacker:dosAttack:2334700212 | 100.0000 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 41 | 0.0000 | 0.8303 | 0.0374 | 1.1082 |
| RS-WeightedTrim | norm-matched | attacker:dataReplay:4623714049 | 71.7949 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8408 | 0.0350 | 0.9067 |
| RS-WeightedTrim | boosted | attacker:dataReplay:4623714049 | 71.7949 | 100.0000 | 0.0000 | 0.0000 | 0.0000 | 59 | 0.0000 | 0.8307 | 0.0365 | 1.0822 |
| RS-WeightedTrim | norm-matched | honest:zeroSpeedReport:9129455203 | 44.0559 | 2.3810 | 0.0000 | 0.0000 | 0.0000 | 113 | 0.0000 | 0.8345 | 0.0377 | 0.9515 |
| RS-WeightedTrim | boosted | honest:zeroSpeedReport:9129455203 | 44.0559 | 2.3810 | 0.0000 | 0.0000 | 0.0000 | 113 | 0.0000 | 0.8306 | 0.0384 | 1.1071 |
| RS-WeightedTrim | norm-matched | honest:feignedBraking:4434209032 | 3.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1 | 0.0000 | 0.8349 | 0.0366 | 0.8962 |
| RS-WeightedTrim | boosted | honest:feignedBraking:4434209032 | 3.3333 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1 | 0.0000 | 0.8311 | 0.0378 | 1.0743 |
| RS-WeightedTrim | norm-matched | honest:trafficCongestionSybil:7802626606 | 78.8889 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 36 | 0.0000 | 0.8317 | 0.0387 | 0.9245 |
| RS-WeightedTrim | boosted | honest:trafficCongestionSybil:7802626606 | 78.8889 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 36 | 0.0000 | 0.8369 | 0.0355 | 1.1181 |
| RS-WeightedTrim | norm-matched | honest:dataReplay:5628007782 | 21.2500 | 76.4706 | 0.0000 | 0.0000 | 0.0000 | 23 | 0.0000 | 0.8344 | 0.0368 | 0.8942 |
| RS-WeightedTrim | boosted | honest:dataReplay:5628007782 | 21.2500 | 76.4706 | 0.0000 | 0.0000 | 0.0000 | 23 | 0.0000 | 0.8316 | 0.0367 | 1.0856 |
| RS-WeightedTrim | norm-matched | honest:randomSpeedOffset:5142823020 | 61.6071 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 28 | 0.0000 | 0.8315 | 0.0375 | 0.9569 |
| RS-WeightedTrim | boosted | honest:randomSpeedOffset:5142823020 | 61.6071 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 28 | 0.0000 | 0.8307 | 0.0374 | 1.1273 |
## Reading the results

- **The noise floor is exactly zero.** Both honest reruns reproduce the
  honest model bit for bit (‖Δθ‖ = 0) and flip no decisions. So every flip
  below is caused by the attacker. (Validation F1 of the rerun reads 0.835
  vs 0.832 only because its temperature is fitted on the 40k validation
  sample rather than the full split.)
- **The stealthy (norm-matched) attack flips nothing** under either
  aggregator: 0 of 10 targets, on seen and unseen messages alike, with
  validation F1, PR-AUC and ECE unchanged. Sending an update the size of an
  honest one wasn't enough for a single RSU out of 20 to move any target's
  decision in 3 rounds.
- **The boosted attack works against FedAvg, but it isn't stealthy.** Mean
  ADDR on unseen messages is 0.33 for attacker targets (wrongly accepted)
  and 0.78 for honest targets (wrongly rejected). The worst cases are 0.95
  and 1.0. The cost is that global validation F1 falls from 0.85 to
  0.33–0.70 and ECE rises from 0.027 to 0.05–0.31. The model moves 15–20
  honest rounds' worth, and any server watching validation metrics would
  notice. The flips are also largely collateral damage from a broken model,
  not a precise targeted flip. On the messages the attacker trained on,
  ADDR is higher (0.77–0.78 mean).
- **Under RS-WeightedTrim, even the boosted attack flips nothing,** and the
  validation metrics don't move (F1 0.831–0.838 vs 0.832). The 20× boosted
  update is trimmed away coordinate by coordinate. The global model moves
  about 1.1 rounds' worth, the same as with the norm-matched attack.
- **Mind which decisions exist.** For the positionMirroring attacker, the
  honest model rejects only 38–50% of its decisions, so the rest are already
  wrong accepts that no attack can make worse. The honest feignedBraking
  vehicle gets 0 (FedAvg) or 1 (RS-WeightedTrim) decisions in the future
  half, so it is left out of the means.

**What this does and doesn't show.** An ADDR of 0 here means *this*
attacker failed. It doesn't prove none can succeed. The attacker is one RSU,
active for 3 rounds, with a fixed recipe (label-flipped target data plus
norm matching or ×20 boosting). An adaptive attacker could do better, for
example by optimising the update directly against the flip objective under
a norm constraint, colluding across several RSUs, or attacking over more
rounds. Row 19 shows how much room such an attacker would have.
