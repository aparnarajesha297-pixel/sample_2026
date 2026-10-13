# Rows 18 and 19: design and checks

The status document describes both rows in one line each, so most choices
below are mine. They are listed here so they can be challenged before
anything is read into the numbers.

## Row 18: ADDR

"If an attacker manipulates only their own submitted model update, carefully
enough that the global accuracy and confidence look normal, how often can
they flip one specific vehicle's accept/reject decision?"

- **Attacker.** One compromised RSU out of 20 (spatial partition, same as
  the poisoning experiment), chosen at random with seed 0. It turned out to
  be RSU 17, which holds 96k training steps.
- **Method.** Targeted model poisoning in the style of Bhagoji et al. (ICML
  2019), "Analyzing federated learning through an adversarial lens". Each
  round the RSU:
  1. computes its honest update;
  2. trains separately from the same global model on its own data plus the
     target's messages with flipped labels, repeated to make up about 20% of
     its training stream;
  3. sends one of two updates:
     - **norm-matched:** the adversarial update rescaled to the honest
       update's norm, so its size looks normal;
     - **boosted:** honest + 20 × (adversarial − honest). This is explicit
       boosting to survive 1/n averaging, and it produces an update far
       larger than normal.
- **When.** 10 honest rounds, then 3 rounds with the attacker active. The
  reference is an honest 3-round continuation from the same checkpoint.
- **Targets.** Chosen before any model was trained: test vehicles
  identified by (run, pseudonym) with at least 50 steps.
  - 5 attackers, one per attack type, with label rate ≥ 0.9. For these the
    flip the adversary wants is *wrongly accepted*.
  - 5 honest vehicles. For these it's *wrongly rejected*.
- **What the attacker knows.** The first half of the target's messages, in
  time. ADDR is reported on the second half, which the attacker never saw
  ("future"), and on the first half as an upper bound ("seen").
- **Decision moments.** The honest model's SVoI controller (H = 3, all four
  evidence actions) runs on each of the target's steps. A step counts only
  if the controller stops there. At those steps, each model's decision is
  Eq. 14 (reject when 100·p > 20·(1 − p)) on its own belief, calibrated on
  validation, which is what the server would do for any new global model.
- **Measures.** Per target: ADDR, split into wrongly accepted and wrongly
  rejected. Across targets: mean and worst case.
- **Stealth.** Validation PR-AUC, F1 (Eq. 14) and ECE of the uncalibrated
  risk, on a fixed 40k-step validation sample, for every model next to the
  honest one. A norm-matched attack that also leaves these unchanged meets
  the "looks normal" condition. A boosted attack is expected to fail it,
  and the report says so where it does.

## Row 19: how far the model can move before decisions flip

- **Base.** The honest continuation from row 18, for each aggregator.
  Calibration is kept at the honest model's temperature.
- **Scale.** ‖Δθ‖ in multiples of the median norm of one honest aggregated
  round update. "1" is one round's worth of change. Tested:
  0.1, 0.3, 1, 3, 10, 30.
- **Directions.**
  - 5 random Gaussian draws.
  - Reversed training (minus the honest 3-round change).
  - Each row-18 attack direction.
  - The first-order worst case: minus the gradient of the detector's loss
    with every honest decision flipped.
- **Measure.** The share of honest decisions that flip, split by
  direction, on a 20k-step test sample, counting only steps where the
  honest controller stops.
- **Link to Theorem 1.** Row 18's measured deviations are placed on the same
  axis. Turning the curve into a guarantee needs the constants of Theorem
  1's deviation bound from the paper. The guide describes the bound but
  doesn't state its formula, so the bound itself isn't computed here.

## Checks done before the real run

- **Determinism.** On multithreaded CPU, two identical federated
  continuations of RAVEN-X-GF ended 0.77 apart in parameter norm under
  FedAvg, from floating-point reduction order alone. That would show up as
  spurious "flips". With `torch.use_deterministic_algorithms(True)`, or a
  single thread, both aggregators give identical models (difference 0.0).
  Both scripts now turn deterministic mode on, and the honest rerun in
  row 18 checks that it holds on the real data. The same effect probably
  explains RAVEN-X-GF's run-to-run difference in the row 6 cross-scenario
  runs.
- **Isolation.** The attacker's extra training runs inside
  `torch.random.fork_rng` and uses its own detector. So the honest clients'
  data order and dropout masks are identical with and without the attack,
  and the only thing that differs is the attacker's update.
- **Smoke test.** Both scripts ran end to end on synthetic data with 4
  RSUs, 1 target per kind, and 1 base and 1 attack round.
