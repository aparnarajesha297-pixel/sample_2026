# Federated RAVEN-X-GF with poisoning (NextGen highway_2)

20 RSUs (spatial partition), 10 rounds x 1 local epoch, 4 malicious RSUs in poisoned runs, one seed.
ΔF1 = F1(no attack) − F1(poisoned), same aggregator. ASR = share of test attack steps the model lets through as benign.

| Aggregator | Poisoning | F1 | Recall | PR-AUC | ECE | ASR | ΔF1 | ΔASR | Comm_MB |
|---|---|---|---|---|---|---|---|---|---|
| FedAvg | none | 0.8747 | 0.7955 | 0.9157 | 0.0335 | 0.2045 | 0.0000 | 0.0000 | 113.3820 |
| FedAvg | label_flip | 0.8546 | 0.7969 | 0.9026 | 0.0516 | 0.2031 | 0.0200 | -0.0013 | 113.3820 |
| FedAvg | sign_flip | 0.3299 | 0.9992 | 0.1757 | 0.5169 | 0.0008 | 0.5448 | -0.2036 | 113.3820 |
| Median | none | 0.8558 | 0.7867 | 0.8979 | 0.0451 | 0.2133 | 0.0000 | 0.0000 | 113.3820 |
| Median | label_flip | 0.8302 | 0.7714 | 0.8885 | 0.0216 | 0.2286 | 0.0256 | 0.0152 | 113.3820 |
| Median | sign_flip | 0.8286 | 0.7805 | 0.8838 | 0.0515 | 0.2195 | 0.0272 | 0.0062 | 113.3820 |
| Krum | none | 0.7076 | 0.6973 | 0.7932 | 0.0985 | 0.3027 | 0.0000 | 0.0000 | 113.3820 |
| Krum | label_flip | 0.6794 | 0.6222 | 0.7467 | 0.0460 | 0.3778 | 0.0282 | 0.0751 | 113.3820 |
| Krum | sign_flip | 0.7691 | 0.6851 | 0.8212 | 0.0667 | 0.3149 | -0.0615 | 0.0122 | 113.3820 |
| ReputationDrop (old rule) | none | 0.8717 | 0.8084 | 0.9102 | 0.0339 | 0.1916 | 0.0000 | 0.0000 | 113.3820 |
| ReputationDrop (old rule) | label_flip | 0.8520 | 0.7946 | 0.9035 | 0.0136 | 0.2054 | 0.0197 | 0.0138 | 113.3820 |
| ReputationDrop (old rule) | sign_flip | 0.8584 | 0.8062 | 0.9083 | 0.0401 | 0.1938 | 0.0134 | 0.0022 | 113.3820 |
| RS-WeightedTrim | none | 0.8672 | 0.7980 | 0.9068 | 0.0451 | 0.2020 | 0.0000 | 0.0000 | 113.3820 |
| RS-WeightedTrim | label_flip | 0.8312 | 0.7750 | 0.8920 | 0.0176 | 0.2250 | 0.0360 | 0.0230 | 113.3820 |
| RS-WeightedTrim | sign_flip | 0.8328 | 0.7779 | 0.8905 | 0.0538 | 0.2221 | 0.0344 | 0.0201 | 113.3820 |

Notes:

- RS-WeightedTrim is the capped-simplex version (kappa = 2, beta_trim = 0.2) that Theorem 1 covers. ReputationDrop is the earlier stand-in and is kept as a baseline.
- FedAvg under sign-flip collapses to flagging almost every vehicle as an attack (recall 0.999, F1 0.33). Its low ASR there reflects that collapse, not robustness.
- Training-time columns in the per-run reports are inflated for runs that shared the CPU with other jobs; about 800 s per configuration is typical.
- One seed per configuration; differences of about 0.02 F1 between the robust aggregators are within run-to-run noise seen elsewhere.
