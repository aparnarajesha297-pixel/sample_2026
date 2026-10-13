# Uncertainty of RAVEN-X-GF

Seeds [0, 1, 2]. Calibrated beliefs from `results/temperature_scaling_nbr` (temperature fitted on validation). u = evidential uncertainty 2/S. Errors are at the validation-chosen F1 threshold. Test split.

## Error rate by uncertainty quintile

| q | mean_u | error_rate |
|---|---|---|
| Q1 | 0.0171 ± 0.0010 | 0.0069 ± 0.0003 |
| Q2 | 0.0350 ± 0.0006 | 0.0232 ± 0.0016 |
| Q3 | 0.0501 ± 0.0014 | 0.0303 ± 0.0035 |
| Q4 | 0.0778 ± 0.0073 | 0.0447 ± 0.0077 |
| Q5 | 0.2508 ± 0.0416 | 0.1194 ± 0.0038 |

## How well uncertainty ranks the model's own errors

'margin' = closeness of the belief to the threshold, which needs no uncertainty head.

| k | AUROC uncertainty → error | AUROC margin → error | AUROC u among honest | AUROC u among attacks | error rate |
|---|---|---|---|---|---|
| all | 0.7476 ± 0.0092 | 0.7163 ± 0.0228 | 0.7986 ± 0.0632 | 0.9437 ± 0.0127 | 0.0449 ± 0.0032 |

## Selective prediction: set aside the most uncertain steps for verification

| Set aside by | Set aside (%) | F1 on rest | Error rate on rest | Attacks set aside (%) |
|---|---|---|---|---|
| uncertainty | 0 | 0.8803 ± 0.0073 | 0.0449 ± 0.0032 | 0.0000 ± 0.0000 |
| margin | 0 | 0.8803 ± 0.0073 | 0.0449 ± 0.0032 | 0.0000 ± 0.0000 |
| uncertainty | 5 | 0.9025 ± 0.0125 | 0.0371 ± 0.0058 | 4.4720 ± 0.8970 |
| margin | 5 | 0.9069 ± 0.0088 | 0.0329 ± 0.0022 | 8.5583 ± 5.3782 |
| uncertainty | 10 | 0.9172 ± 0.0109 | 0.0325 ± 0.0051 | 7.1772 ± 0.8375 |
| margin | 10 | 0.8994 ± 0.0425 | 0.0305 ± 0.0041 | 19.8769 ± 17.4317 |
| uncertainty | 20 | 0.9379 ± 0.0061 | 0.0263 ± 0.0030 | 11.2076 ± 0.6250 |
| margin | 20 | 0.6128 ± 0.5310 | 0.0291 ± 0.0060 | 46.7950 ± 37.2419 |
| uncertainty | 30 | 0.9509 ± 0.0038 | 0.0230 ± 0.0020 | 14.2790 ± 0.4567 |
| margin | 30 | 0.3467 ± 0.5246 | 0.0265 ± 0.0027 | 64.4687 ± 43.8804 |

## Uncertainty and errors by attack type (sorted by mean u)

| index | mean_u | error_rate |
|---|---|---|
| Sudden Stop | 0.2362 ± 0.0767 | 0.2316 ± 0.1327 |
| Acceleration Multiplication | 0.1947 ± 0.0098 | 0.2282 ± 0.0432 |
| Position Mirroring | 0.1414 ± 0.0043 | 0.5328 ± 0.0166 |
| Data Replay | 0.1179 ± 0.0304 | 0.2841 ± 0.0172 |
| benign | 0.0938 ± 0.0121 | 0.0155 ± 0.0045 |
| Time Delay | 0.0888 ± 0.0128 | 0.9888 ± 0.0062 |
| Feigned Braking | 0.0822 ± 0.0056 | 0.1168 ± 0.0130 |
| Sudden Constant Speed | 0.0818 ± 0.0164 | 0.1031 ± 0.0210 |
| Constant Speed Offset | 0.0489 ± 0.0091 | 0.0758 ± 0.0028 |
| Constant Position Offset | 0.0454 ± 0.0038 | 0.2294 ± 0.0119 |
| Zero Speed Report | 0.0389 ± 0.0072 | 0.0379 ± 0.0051 |
| Random Speed Offset | 0.0372 ± 0.0017 | 0.0661 ± 0.0014 |
| Reversed Heading | 0.0294 ± 0.0032 | 0.0617 ± 0.0005 |
| Random Position Offset | 0.0220 ± 0.0015 | 0.0213 ± 0.0016 |
| Traffic Congestion Sybil | 0.0096 ± 0.0012 | 0.0000 ± 0.0000 |
| DoS | 0.0084 ± 0.0004 | 0.0000 ± 0.0000 |

## TRUST / VERIFY / REJECT on calibrated outputs

Fitted on validation per seed (mean thresholds: t_low = 0.038, t_high = 0.356, u_max = 0.1520; reject precision ≥ 0.98, attack share among TRUST ≤ 0.02, u above its validation 90% quantile → VERIFY).

| decision | share | attack_rate_in_bucket | share_of_all_attacks | share_of_all_benign |
|---|---|---|---|---|
| TRUST | 0.5394 ± 0.0387 | 0.0248 ± 0.0002 | 0.0678 ± 0.0050 | 0.6555 ± 0.0470 |
| VERIFY | 0.2936 ± 0.0397 | 0.0816 ± 0.0071 | 0.1205 ± 0.0081 | 0.3362 ± 0.0479 |
| REJECT | 0.1670 ± 0.0027 | 0.9601 ± 0.0095 | 0.8117 ± 0.0050 | 0.0083 ± 0.0021 |
## Reading the results

- **Errors pile up where uncertainty is high.** The error rate rises
  steadily from 0.7% in the least uncertain fifth of steps to 11.9% in the
  most uncertain fifth.
- **Uncertainty picks out the model's own mistakes** with AUROC 0.75. The
  simple "belief close to the threshold" margin manages 0.72. Uncertainty
  is especially good on attack steps (0.94 among attacks, 0.80 among honest
  steps).
- **Setting the most uncertain steps aside works, and the margin doesn't.**
  Sending the 10% most uncertain steps to verification lifts F1 on the rest
  from 0.880 to 0.917; at 30% it reaches 0.951. The same set-aside by
  margin is unstable across seeds: at 20–30% it sometimes removes most of
  the attacks (F1 0.61 ± 0.53). Uncertainty is the safer signal to route on.
- **Uncertainty misses attacks the model is confidently wrong about.** Time
  Delay is missed 99% of the time with *lower* uncertainty than honest
  traffic (0.089 vs 0.094). Constant Position Offset is missed 23% of the
  time with low uncertainty. Uncertainty flags the hard cases the model
  recognises (Sudden Stop, Acceleration Multiplication, Position Mirroring,
  Data Replay), but not attacks it has never learned to see.
- **TRUST / VERIFY / REJECT:** REJECT is 96% precise and catches 81% of
  attacks. TRUST lets 6.8% of attacks through. VERIFY takes 29% of traffic,
  mostly honest vehicles (34% of all honest steps), which is the cost of
  routing on uncertainty.
