# G5 feature check

Row 13's last group (G5 = RelativeSpeed, RelativeHeading) compares the sender with the receiver. The status document's row 13 instead ends with a neighbour-disagreement group, which was not tested. This checks G5's correctness, why it does not help, and whether neighbour disagreement does.

## 1. Data checks

- Recomputed from raw fields, max |difference|: RelativeSpeed 0.0e+00, RelativeHeading 4.6e-05.
- Heading convention: honest sender heading within 10° of the compass bearing of its motion in 94% of moving steps; receiver heading in 88%. Same convention (0° = north, clockwise).
- Honest RelativeHeading on train, share in 0–30 / 30–60 / 60–120 / 120–150 / 150–180°: 0.23 / 0.10 / 0.40 / 0.09 / 0.19. Many crossing directions: the scenario has ramps and crossing roads within range.

Single-feature informativeness and drift:

| Feature | Group | |AUC - 0.5| (train) | KS train vs val | KS train vs test |
|---|---|---|---|---|
| MessageGap | G1-G4 | 0.1665 | 0.0133 | 0.0058 |
| NbrNearestDist | neighbour | 0.1536 | 0.1336 | 0.1967 |
| NbrCount | neighbour | 0.1525 | 0.1334 | 0.1884 |
| PositionChange | G1-G4 | 0.1431 | 0.0603 | 0.0801 |
| HeadingInconsistency | G1-G4 | 0.1119 | 0.0127 | 0.0564 |
| AccelerationInconsistency | G1-G4 | 0.0741 | 0.0140 | 0.0395 |
| RoadEdgeDist | G1-G4 | 0.0715 | 0.0634 | 0.0465 |
| NbrSpeedDev | neighbour | 0.0536 | 0.1343 | 0.1860 |
| NbrHeadingMisalign | neighbour | 0.0463 | 0.1384 | 0.1909 |
| MsgCount | G1-G4 | 0.0329 | 0.0015 | 0.0020 |
| HeadingChange | G1-G4 | 0.0311 | 0.0124 | 0.1212 |
| Speed | G1-G4 | 0.0280 | 0.0725 | 0.0999 |
| RelativeSpeed | G5 | 0.0276 | 0.0314 | 0.0618 |
| SpeedChange | G1-G4 | 0.0174 | 0.0123 | 0.0804 |
| rx_spd | receiver | 0.0105 | 0.0750 | 0.1016 |
| rx_hed | receiver | 0.0073 | 0.0919 | 0.2751 |
| Acceleration | G1-G4 | 0.0070 | 0.0200 | 0.0923 |
| Heading | G1-G4 | 0.0056 | 0.0943 | 0.2687 |
| Jerk | G1-G4 | 0.0056 | 0.0097 | 0.0175 |
| SpeedInconsistency | G1-G4 | 0.0047 | 0.0154 | 0.1233 |
| DistanceToReceiver | G1-G4 | 0.0046 | 0.0423 | 0.1544 |
| RelativeHeading | G5 | 0.0044 | 0.0320 | 0.1241 |
| TimeLag | G1-G4 | 0.0031 | 0.0142 | 0.0117 |

Receiver speed 10th / 50th / 90th percentile (m/s): train 8.0 / 14.6 / 40.3, val 5.5 / 14.0 / 32.8, test 8.2 / 14.0 / 54.7.

## 2. Retraining (test, mean ± std over seeds [0, 1, 2]; thresholds on validation)

### RAVEN-X-GF

| Variant | Features | F1 | Recall | Precision | PR-AUC | ROC-AUC | ECE | ΔF1 vs G4 | ΔPR-AUC vs G4 |
|---|---|---|---|---|---|---|---|---|---|
| G4 | 15 | 0.8808 ± 0.0053 | 0.8434 ± 0.0040 | 0.9217 ± 0.0160 | 0.9196 ± 0.0011 | 0.9451 ± 0.0009 | 0.0316 ± 0.0054 | +0.0000 | +0.0000 |
| G4 + G5 | 17 | 0.8775 ± 0.0091 | 0.8411 ± 0.0049 | 0.9176 ± 0.0256 | 0.9186 ± 0.0016 | 0.9445 ± 0.0003 | 0.0258 ± 0.0127 | -0.0033 | -0.0010 |
| G4 + receiver state | 17 | 0.8807 ± 0.0067 | 0.8379 ± 0.0018 | 0.9283 ± 0.0169 | 0.9191 ± 0.0012 | 0.9444 ± 0.0006 | 0.0369 ± 0.0115 | -0.0000 | -0.0005 |
| G4 + neighbour | 19 | 0.8805 ± 0.0073 | 0.8338 ± 0.0033 | 0.9330 ± 0.0185 | 0.9184 ± 0.0017 | 0.9440 ± 0.0011 | 0.0237 ± 0.0116 | -0.0002 | -0.0011 |
| G4 + G5 + neighbour | 21 | 0.8818 ± 0.0019 | 0.8332 ± 0.0019 | 0.9364 ± 0.0067 | 0.9171 ± 0.0030 | 0.9440 ± 0.0026 | 0.0311 ± 0.0065 | +0.0010 | -0.0025 |

### XGBoost

| Variant | Features | F1 | Recall | Precision | PR-AUC | ROC-AUC | ECE | ΔF1 vs G4 | ΔPR-AUC vs G4 |
|---|---|---|---|---|---|---|---|---|---|
| G4 | 15 | 0.8121 ± 0.0013 | 0.7640 ± 0.0059 | 0.8668 ± 0.0103 | 0.8595 ± 0.0007 | 0.9069 ± 0.0007 | 0.0161 ± 0.0019 | +0.0000 | +0.0000 |
| G4 + G5 | 17 | 0.7962 ± 0.0032 | 0.7680 ± 0.0093 | 0.8269 ± 0.0158 | 0.8547 ± 0.0009 | 0.9062 ± 0.0001 | 0.0312 ± 0.0023 | -0.0159 | -0.0048 |
| G4 + receiver state | 17 | 0.8130 ± 0.0010 | 0.7575 ± 0.0067 | 0.8774 ± 0.0067 | 0.8593 ± 0.0008 | 0.9053 ± 0.0001 | 0.0238 ± 0.0017 | +0.0009 | -0.0002 |
| G4 + neighbour | 19 | 0.8583 ± 0.0009 | 0.7823 ± 0.0042 | 0.9508 ± 0.0082 | 0.8812 ± 0.0004 | 0.9148 ± 0.0004 | 0.0188 ± 0.0019 | +0.0462 | +0.0217 |
| G4 + G5 + neighbour | 21 | 0.8432 ± 0.0066 | 0.7870 ± 0.0029 | 0.9081 ± 0.0191 | 0.8798 ± 0.0003 | 0.9150 ± 0.0002 | 0.0335 ± 0.0019 | +0.0311 | +0.0203 |

### XGBoost feature importance (gain share, all 21 features, mean over seeds)

| index | importance |
|---|---|
| NbrNearestDist | 0.1411 |
| PositionChange | 0.1348 |
| SpeedInconsistency | 0.1300 |
| NbrCount | 0.1146 |
| HeadingInconsistency | 0.0794 |
| AccelerationInconsistency | 0.0708 |
| MessageGap | 0.0648 |
| MsgCount | 0.0647 |
| RoadEdgeDist | 0.0418 |
| Acceleration | 0.0325 |
| Jerk | 0.0310 |
| SpeedChange | 0.0228 |
| Speed | 0.0137 |
| NbrHeadingMisalign | 0.0118 |
| HeadingChange | 0.0107 |
| RelativeHeading | 0.0088 |
| Heading | 0.0079 |
| RelativeSpeed | 0.0067 |
| DistanceToReceiver | 0.0054 |
| NbrSpeedDev | 0.0039 |
| TimeLag | 0.0029 |
## Reading the results

- **G5 is computed correctly.** There's no bug. Sender and receiver headings
  use the same convention, and the stored values match a recomputation.
- **G5 carries almost no signal.** On its own, `RelativeHeading` is barely
  better than chance (|AUC − 0.5| = 0.004), and `RelativeSpeed` scores the
  same as `Speed` (0.028) because it's `Speed` minus the receiver's speed.
  It also drifts between train and test (KS 0.06 and 0.12), while barely
  drifting between train and validation (0.03).
- **For XGBoost, G5 hurts through calibration, not ranking.** F1 drops
  0.016, from 0.812 to 0.796, and precision from 0.867 to 0.827. PR-AUC
  barely moves (−0.005), but ECE doubles (0.016 → 0.031). The threshold
  picked on validation fits test worse once G5 is in, which matches G5
  drifting between validation and test. Adding the raw receiver speed and
  heading instead is neutral (+0.001 F1). So what hurts is how G5
  combines sender and receiver state, not the receiver state itself.
- **RAVEN-X-GF is indifferent to every variant.** All five F1 values sit
  within ±0.003 of each other, well inside the seed spread. That includes
  the neighbour group, as expected: the graph edges already give it each
  neighbour's distance, speed difference and heading agreement.
- **The neighbour-disagreement group the status document describes helps
  XGBoost a lot.** F1 rises 0.046 (0.812 → 0.858), PR-AUC rises 0.022, and
  precision reaches 0.951. Distance to the nearest neighbour and the
  neighbour count become its two most important features. This narrows the
  F1 gap between XGBoost and RAVEN-X-GF from 0.069 to 0.022. Adding G5 on
  top takes back part of the gain (0.843).
- **A caveat on the neighbour features:** they drift more than any other
  group between train and test (KS 0.19), because traffic density differs
  between runs. They help anyway, but they're the features most likely to
  behave differently in a new scenario. I haven't broken the gain down by
  attack type. My guess, which is untested, is that most of it comes from
  Sybil ghosts sitting unusually close to other vehicles.

**Recommendation.** Drop G5 from the feature set, since it helps no model
and hurts XGBoost, and add the four neighbour-disagreement features in its
place. That makes the tabular baselines a fairer comparison for the graph
models, and it's what the status document describes for row 13. The change
alters every model's inputs, though, so it would mean re-running the
headline tables. That's a decision for you, not something I've changed.
