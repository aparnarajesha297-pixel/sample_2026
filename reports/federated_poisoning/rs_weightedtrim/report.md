# Federated RAVEN-X (nextgen data)

20 RSUs (spatial partition), 10 rounds x 1 local epoch(s), 4 malicious RSUs in poisoned runs.

| Aggregator | Poisoning | Accuracy | F1 | Recall | PR-AUC | ECE | ASR | Comm_MB | TrainTime_s | ΔF1 | ΔASR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RS-WeightedTrim | none | 0.9517 | 0.8672 | 0.7980 | 0.9068 | 0.0451 | 0.2020 | 113.3820 | 17570.4839 | 0.0000 | 0.0000 |
| RS-WeightedTrim | label_flip | 0.9378 | 0.8312 | 0.7750 | 0.8920 | 0.0176 | 0.2250 | 113.3820 | 830.5953 | 0.0360 | 0.0230 |
| RS-WeightedTrim | sign_flip | 0.9383 | 0.8328 | 0.7779 | 0.8905 | 0.0538 | 0.2221 | 113.3820 | 823.3024 | 0.0344 | 0.0201 |
