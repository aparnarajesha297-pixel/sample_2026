# Data-loader sanity check (row 21) and Data Replay / Position Mirroring status (row 4b)

## Row 21: does the loader read NextGen correctly?

Data under `/home/user/data/nextgen`: highway_2 (all receivers), urban_2 (15 %
of receivers), highway_7 (3 % of receivers), all 15 attacks each.

Path parsing, checked against the folder each file sits in (22,875 JSON files):

| check | result |
|---|---|
| split parsed correctly | 100 % |
| attack parsed correctly | 100 % |
| scenario parsed correctly | 100 % |
| files with no split / attack | 0 / 0 |
| empty files | 0 |
| files per attack equal within a scenario | yes (highway_2 1,110; urban_2 376; highway_7 39) |

Attacker share, against NextGen's documented 20 % attacker density (a share of vehicles):

| scenario | messages | attack messages | attacker vehicles (median over subsets) |
|---|---|---|---|
| highway_2 | 1,633,604 | 22.2 % | 19.9 % |
| urban_2 | 1,988,239 | 22.1 % | 19.9 % |
| highway_7 | 2,393,125 | 20.6 % | 20.0 % |

The vehicle share matches the documented 20 %. Message share per attack differs
for known reasons: DoS and Traffic Congestion Sybil add fabricated messages
(44–50 %), while gradual attacks label only messages that deviate significantly
(Sudden Constant Speed 1.6–3.7 %, Feigned Braking 5–8 %, Acceleration
Multiplication 7–11 %).

## Row 4b: Data Replay and Position Mirroring (highway_2, all 15 attacks, 10 seeds, F1 mean ± std)

| model | Data Replay | Position Mirroring |
|---|---|---|
| Random Forest | 0.363 ± 0.001 | 0.313 ± 0.008 |
| XGBoost | 0.352 ± 0.003 | 0.319 ± 0.008 |
| GRU | 0.777 ± 0.011 | 0.609 ± 0.017 |
| GAT | 0.275 ± 0.008 | 0.273 ± 0.019 |
| RAVEN-X | 0.792 ± 0.013 | 0.579 ± 0.015 |
| RAVEN-X-GF | 0.781 ± 0.013 | 0.621 ± 0.024 |

Neither attack should be reported as "fixed". No feature change targeted them.
Both are detected only by models that see message history (GRU, RAVEN-X,
RAVEN-X-GF); single-snapshot models stay at 0.27–0.36. Data Replay reaches
about 0.78–0.79 F1. Position Mirroring stays the weakest attack after Time
Delay, at 0.58–0.62 F1.
