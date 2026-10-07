# Temperature scaling

Data: nextgen. Seeds: [0, 1, 2]. T learned on the validation split (min NLL) and applied unchanged to test; F1 threshold re-chosen on validation.

| Model | T | ECE before | ECE after | Brier before | Brier after | NLL before | NLL after | F1 before | F1 after |
|---|---|---|---|---|---|---|---|---|---|
| GRU [softmax] | 1.051 ± 0.071 | 0.0283 ± 0.0042 | 0.0282 ± 0.0042 | 0.0438 ± 0.0011 | 0.0439 ± 0.0011 | 0.1775 ± 0.0054 | 0.1759 ± 0.0040 | 0.8788 ± 0.0044 | 0.8788 ± 0.0044 |
| GAT [softmax] | 1.056 ± 0.003 | 0.0157 ± 0.0055 | 0.0136 ± 0.0059 | 0.0495 ± 0.0016 | 0.0494 ± 0.0016 | 0.1962 ± 0.0080 | 0.1951 ± 0.0075 | 0.8451 ± 0.0011 | 0.8451 ± 0.0011 |
| RAVEN-X [evidential] | 0.848 ± 0.038 | 0.0299 ± 0.0077 | 0.0272 ± 0.0083 | 0.0478 ± 0.0060 | 0.0479 ± 0.0060 | 0.1857 ± 0.0234 | 0.1866 ± 0.0239 | 0.8700 ± 0.0124 | 0.8698 ± 0.0123 |
| RAVEN-X [softmax] | 13.724 ± 1.112 | 0.0531 ± 0.0066 | 0.0539 ± 0.0147 | 0.0533 ± 0.0065 | 0.0497 ± 0.0069 | 0.6832 ± 0.1054 | 0.2058 ± 0.0367 | 0.8711 ± 0.0124 | 0.8711 ± 0.0124 |
| RAVEN-X-GF [evidential] | 0.800 ± 0.051 | 0.0237 ± 0.0116 | 0.0180 ± 0.0125 | 0.0422 ± 0.0059 | 0.0423 ± 0.0060 | 0.1672 ± 0.0173 | 0.1676 ± 0.0179 | 0.8805 ± 0.0073 | 0.8803 ± 0.0073 |
| RAVEN-X-GF [softmax] | 11.962 ± 0.466 | 0.0462 ± 0.0076 | 0.0369 ± 0.0191 | 0.0464 ± 0.0073 | 0.0428 ± 0.0065 | 0.6112 ± 0.0515 | 0.1742 ± 0.0211 | 0.8797 ± 0.0049 | 0.8797 ± 0.0049 |

## Other metrics

| Model | Precision before | Precision after | Recall before | Recall after | PR-AUC before | PR-AUC after | ROC-AUC before | ROC-AUC after |
|---|---|---|---|---|---|---|---|---|
| GRU [softmax] | 0.9295 ± 0.0102 | 0.9295 ± 0.0102 | 0.8334 ± 0.0024 | 0.8334 ± 0.0024 | 0.9165 ± 0.0028 | 0.9165 ± 0.0028 | 0.9427 ± 0.0016 | 0.9427 ± 0.0016 |
| GAT [softmax] | 0.9373 ± 0.0088 | 0.9373 ± 0.0088 | 0.7695 ± 0.0047 | 0.7695 ± 0.0047 | 0.8777 ± 0.0006 | 0.8777 ± 0.0006 | 0.9141 ± 0.0019 | 0.9141 ± 0.0019 |
| RAVEN-X [evidential] | 0.9146 ± 0.0339 | 0.9139 ± 0.0334 | 0.8300 ± 0.0074 | 0.8303 ± 0.0072 | 0.9152 ± 0.0043 | 0.9152 ± 0.0043 | 0.9443 ± 0.0023 | 0.9443 ± 0.0023 |
| RAVEN-X [softmax] | 0.9183 ± 0.0316 | 0.9183 ± 0.0316 | 0.8289 ± 0.0056 | 0.8289 ± 0.0056 | 0.8972 ± 0.0243 | 0.9152 ± 0.0042 | 0.9425 ± 0.0043 | 0.9442 ± 0.0023 |
| RAVEN-X-GF [evidential] | 0.9330 ± 0.0185 | 0.9303 ± 0.0189 | 0.8338 ± 0.0033 | 0.8356 ± 0.0059 | 0.9184 ± 0.0017 | 0.9184 ± 0.0017 | 0.9440 ± 0.0011 | 0.9440 ± 0.0011 |
| RAVEN-X-GF [softmax] | 0.9266 ± 0.0077 | 0.9266 ± 0.0077 | 0.8373 ± 0.0039 | 0.8373 ± 0.0039 | 0.9119 ± 0.0046 | 0.9183 ± 0.0016 | 0.9434 ± 0.0012 | 0.9440 ± 0.0011 |
## Reading the results (19 features)

- The evidential rows are the models' own outputs. The "[softmax]" rows
  read the same evidential head as if it were a softmax and need a huge
  temperature (T ≈ 12–14), so they're only a cross-check.
- RAVEN-X-GF is slightly over-confident (T = 0.80). Temperature scaling
  lowers its ECE from 0.024 to 0.018 without changing F1 (0.880). It has
  the best Brier score of all models (0.042) and the best NLL (0.168).
- GAT has the lowest ECE (0.014 after scaling), but much lower F1 (0.845).
  GRU's ECE (0.028) is unchanged by scaling (T = 1.05).
- Compared with the 17-feature run, RAVEN-X-GF's ECE after scaling went
  from 0.027 to 0.018, its Brier score from 0.046 to 0.042, and its F1
  from 0.876 to 0.880.
