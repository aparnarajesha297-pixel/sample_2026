# RAVEN-X experiments

Code for the RAVEN-X misbehaviour-detection experiments on VeReMi NextGen:
Experiment 1 (detection, risk and uncertainty), the cross-scenario tests,
Experiment 3 (federated learning and poisoning) and Experiment 4
(scalability). The mobility-horizon experiment (SUMO) and the blockchain
handoff are not implemented here.

The central question is whether RAVEN-X can spot a malicious vehicle from
three kinds of evidence:

- what the vehicle reports right now (speed, heading, acceleration, how its
  position moved since the last message),
- how those reports change over time,
- how they compare with what the vehicles around it report.

Picture A claiming 120 km/h while B, C, D and E all report around 65 km/h.
Any one of those signals might be explained away. All three together are hard
to ignore.

## Setup

```bash
pip install -r requirements.txt
python -m pytest -q          # 12 fast checks, about 5 s
```

No torch-geometric is needed; the GAT layer is written in plain PyTorch
(`ravenx/models/nn.py`). Everything runs on CPU.

## Data

Two sources, same schema, same code path after loading:

`--data nextgen --root <folder>` reads the real VeReMi NextGen JSON files
(`rcvTime`, `sendTime`, `sender_alias`, `sender.pos/spd/hed/acl`,
`attacker`). Split, attack type and scenario are taken from the folder names;
one JSON file is treated as one receiving vehicle's log. If the folder names
do not say low or high density, pass `--density-map highway_1=low,...`. The
official train / val / test split is used as is, never re-split.

`--data synthetic` (the default) generates logs in the same format: urban
grid and highway roads, low and high density, three driver profiles, 20 %
attackers, all 15 NextGen attacks injected on a shared base trace, test
drawn from a separate map region. **It exists to develop and debug the
pipeline without the 36 GB download. Numbers from it are not results.**
Every report written from synthetic data says so at the top.

Receivers only see pseudonyms, so every stream is keyed on
`(receiver, sender_alias)`. The true `sender_id` is never a feature.

### What a model classifies

A *step* is one sender's stream, as heard by one receiver, in one 1-second
bin. With 1 Hz CAMs a step is one message; during a DoS flood it is the last
message plus a count. All models classify the same steps with the same 11
features, so any gap between models comes from the architecture:

| model | sees |
|---|---|
| Random Forest, XGBoost | the current step only |
| GRU | the last T = 10 steps of the stream |
| GAT | the current step plus the other vehicles the receiver heard in the same second, within 150 m |
| RAVEN-X | GAT at each of the last 10 steps, then a GRU, then an evidential head that outputs risk and uncertainty |
| GAT+GRU (ablation) | RAVEN-X with an ordinary softmax head |

Features: Speed, Heading, Acceleration, PositionChange, SpeedChange,
HeadingChange, SpeedError (position-derived speed vs reported speed),
MessageGap, AccelError, TimeLag (receive time minus claimed send time) and
MsgCount. The last three are additions to the plan's list. Without them,
time-delay and flooding attacks can't be seen from a single message.

## Running the experiments

The plan recommends growing the problem step by step, and every script takes
the same data flags, so that is just a flag:

```bash
# step 1: one attack
python scripts/run_exp1.py --data nextgen --root /data/NextGen --attacks constantPositionOffset
# step 2: four attacks
python scripts/run_exp1.py ... --attacks constantPositionOffset constantSpeedOffset dosAttack dataReplay
# step 3: all 15 (default), three seeds for mean ± std
python scripts/run_exp1.py ... --seeds 0 1 2
```

| plan phase | script | main outputs |
|---|---|---|
| 1-5 data, features, sequences, graph | `scripts/prepare_data.py` | `processed_data.csv`, `features.csv`, `sequence_dataset.pkl`, `edges.csv`, `graph_stats.csv`, `dataset_summary.json` |
| 6-9 Experiment 1 | `scripts/run_exp1.py` | `report.md`, detection and calibration tables, `attackwise_*.csv`, `risk_distribution.png`, `uncertainty_distribution.png`, `risk_uncertainty_decision.png`, `reliability_diagram.png`, `ravenx_model.pt` |
| 10 cross-scenario | `scripts/run_cross_scenario.py` | `report.md`, per-test F1 / Recall / PR-AUC / ECE next to the in-domain score |
| 12-13 federated + poisoning | `scripts/run_federated.py` | `report.md`, accuracy / F1 / recall / comm cost / time, ΔF1 and ASR per aggregator |
| 14 scalability | `scripts/run_scalability.py` | `scalability.csv`, `vehicles_vs_{latency,cpu,memory,graph_time}.png` |

Everything goes to `results/<experiment>/`. Prepared data is cached in
`cache/`, keyed by the data flags.

## How each research question maps to the output

**Q1, can we detect attacks at all?** The detection table in
`results/exp1/report.md`: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC
for all five models. The decision threshold is picked on validation (max F1)
and applied unchanged to test.

**Q2, does time help?** GRU against the better of RF and XGBoost. **Q3, do
neighbours help?** GAT against the same baseline. **Q4, does the
combination help?** RAVEN-X against GRU and against GAT. The report prints
ΔF1 and ΔPR-AUC for each pair. Run with `--seeds 0 1 2` or more and only
claim a gain that is clearly bigger than the spread between seeds.

**Q5, is the model trustworthy?** ECE and Brier for every model, a
reliability diagram, and `uncertainty_vs_error.csv`, which splits the test
set into uncertainty quintiles and reports the error rate in each. If the
uncertainty means anything, the error rate should climb from Q1 to Q5.

**Risk decisions.** Uncertainty here is the evidential vacuity, K / S.
`decision_policy.json` holds three thresholds fitted on validation:
`t_high` (confident REJECTs reach 98 % precision), `t_low` (at most 2 % of
confident TRUSTs are attacks) and `u_max` (the 90th percentile of
validation uncertainty). Anything in between, or too uncertain, becomes
VERIFY. The plan's fixed 0.30 / 0.80 levels are reported next to the tuned
policy for comparison.

**Per attack.** `attackwise_ravenx.csv` and `attackwise_f1.csv` show
precision / recall / F1 for each of the 15 attacks. Each NextGen subset holds
one attack plus its benign traffic, so a row is that subset's test data.

**Generalisation.** `run_cross_scenario.py` trains on urban and tests on
highway, trains on low density and tests on high, and runs every ordered
scenario pair. Each row carries the in-domain score as well, so the drop is
visible. Neural inputs are re-normalised with source-domain statistics only.

**Federated.** Training steps are split between 20 RSUs by receiver (k-means
on position by default; `--partition random` or `attack` for IID and
strongly non-IID), so whole streams and graph snapshots stay local. Each
round, every RSU trains locally and sends a parameter delta, and the server
aggregates with FedAvg, coordinate-wise Median, Krum or RS-WeightedTrim.
Poisoning runs make 4 RSUs malicious, either by flipping attack labels to
benign or by sending −3× their honest update. ΔF1 compares against the same
aggregator without poisoning. ASR is the share of test attack steps the
poisoned model lets through as benign.

**Scalability.** N vehicles in one 1 km² RSU area, N from 10 to 1000.
Measures feature and graph construction time, inference latency (mean, P95,
P99), CPU and memory. Latency covers recomputing the whole 10-step window
every time, which makes it an upper bound; an RSU that caches each second's
graph embedding would be cheaper.

## Things to settle before reporting

- **RS-WeightedTrim.** The plan names it but doesn't define it. The version
  in `ravenx/federated.py` scores each update by cosine similarity to the
  coordinate-wise median and keeps a running reputation. It drops the
  lowest-reputation 20 %, clips the rest to the median norm and averages them
  weighted by reputation × data size. Swap in the paper's definition if it
  differs.
- **Flower.** The federated run is a single-process simulation. The
  aggregators are plain functions over the update matrix, so they drop into
  a Flower `Strategy.aggregate_fit` unchanged. I didn't wire that up because
  the simulation gives the same numbers with fewer moving parts.
- **Neighbour radius (150 m) and bin length (1 s)** are guesses from the plan's
  "d < R" rule. Both are flags (`--radius`, `--bin`); tune them on validation.
- **NextGen folder layout.** The loader infers metadata from paths. Check the
  first `prepare_data.py` checkpoint (message count, attack share around 20 %)
  before trusting anything downstream.
