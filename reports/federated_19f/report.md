# Federated RAVEN-X (nextgen data)

20 RSUs (spatial partition), 10 rounds x 1 local epoch(s), 4 malicious RSUs in poisoned runs.

| Aggregator | Poisoning | Accuracy | F1 | Recall | PR-AUC | ECE | ASR | Comm_MB | TrainTime_s | ΔF1 | ΔASR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FedAvg | none | 0.9550 | 0.8735 | 0.7867 | 0.9151 | 0.0308 | 0.2133 | 113.7726 | 1195.4491 | 0.0000 | 0.0000 |
| FedAvg | label_flip | 0.9423 | 0.8403 | 0.7686 | 0.8919 | 0.0517 | 0.2314 | 113.7726 | 1131.9180 | 0.0332 | 0.0181 |
| FedAvg | sign_flip | 0.1976 | 0.3299 | 1.0000 | 0.1895 | 0.5180 | 0.0000 | 113.7726 | 1157.5405 | 0.5436 | -0.2132 |
| Median | none | 0.9412 | 0.8441 | 0.8054 | 0.9007 | 0.0457 | 0.1946 | 113.7726 | 1167.7679 | 0.0000 | 0.0000 |
| Median | label_flip | 0.9400 | 0.8383 | 0.7868 | 0.8931 | 0.0186 | 0.2132 | 113.7726 | 1203.7490 | 0.0058 | 0.0185 |
| Median | sign_flip | 0.9338 | 0.8213 | 0.7709 | 0.8827 | 0.0663 | 0.2291 | 113.7726 | 1165.9434 | 0.0228 | 0.0345 |
| Krum | none | 0.9099 | 0.7602 | 0.7231 | 0.8279 | 0.0450 | 0.2769 | 113.7726 | 1127.1447 | 0.0000 | 0.0000 |
| Krum | label_flip | 0.8724 | 0.6616 | 0.6317 | 0.7232 | 0.1011 | 0.3683 | 113.7726 | 1096.0560 | 0.0986 | 0.0913 |
| Krum | sign_flip | 0.9077 | 0.7285 | 0.6269 | 0.8093 | 0.1149 | 0.3731 | 113.7726 | 1121.2922 | 0.0317 | 0.0962 |
| RS-WeightedTrim | none | 0.9523 | 0.8691 | 0.8011 | 0.9120 | 0.0401 | 0.1989 | 113.7726 | 1120.5619 | 0.0000 | 0.0000 |
| RS-WeightedTrim | label_flip | 0.9411 | 0.8404 | 0.7850 | 0.8971 | 0.0137 | 0.2150 | 113.7726 | 1107.6438 | 0.0287 | 0.0161 |
| RS-WeightedTrim | sign_flip | 0.9339 | 0.8253 | 0.7906 | 0.8902 | 0.0594 | 0.2094 | 113.7726 | 1140.4201 | 0.0438 | 0.0105 |
| ReputationDrop | none | 0.9532 | 0.8718 | 0.8054 | 0.9133 | 0.0330 | 0.1946 | 113.7726 | 1093.5184 | 0.0000 | 0.0000 |
| ReputationDrop | label_flip | 0.9452 | 0.8537 | 0.8095 | 0.9079 | 0.0150 | 0.1905 | 113.7726 | 1106.3543 | 0.0181 | -0.0041 |
| ReputationDrop | sign_flip | 0.9500 | 0.8636 | 0.8012 | 0.9109 | 0.0361 | 0.1988 | 113.7726 | 1106.7440 | 0.0082 | 0.0042 |

Model: RAVEN-X-GF with the 19 features, deterministic training, one seed.
Centralised RAVEN-X-GF for reference: F1 0.880 ± 0.007 (10 seeds).

## Reading the results

- **Without poisoning, federated training costs little.** FedAvg reaches
  F1 0.874 and RS-WeightedTrim 0.869, against 0.880 centralised. Median
  (0.844) and especially Krum (0.760) lose accuracy even with no attacker,
  because they discard most of the honest updates on non-IID spatial data.
- **FedAvg collapses under sign-flip poisoning.** F1 drops to 0.33: it flags
  every vehicle (recall 1.0, ASR 0 only because of that collapse).
- **RS-WeightedTrim holds under both attacks.** The F1 drop is 0.029 for
  label flip and 0.044 for sign flip; ASR rises by at most 0.016. This is the
  rule Theorem 1 covers.
- **ReputationDrop, the old rule, degrades least.** The drop is 0.018 and
  0.008, but Theorem 1 doesn't cover it. Median also holds (0.006 and
  0.023) but starts lower.
- **Krum is the weakest.** It loses 0.10 under label flip, from an already
  low baseline.
- One seed per configuration. Differences of about 0.02 F1 between the
  robust rules are within the run-to-run spread seen elsewhere, so only the
  large effects (FedAvg's collapse, Krum's weakness) are firm.
