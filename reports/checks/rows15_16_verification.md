# Rows 15 and 16: checks before implementation

These checks were run on highway_2, validation split unless noted, before
any code was written. They explain why both rows use slightly different
stand-ins from the ones the status document suggests.

## Row 15: mobility-aware horizon

The status document suggests using "time left in the vehicle's current
recorded session" as a stand-in for "time until it leaves range", then
reporting the proxy's MAE/RMSE against the actual time left.

What the data shows:

1. **The session time left can't be both the proxy and the truth.** If it's
   used directly, the MAE is zero by construction. It's also only known after
   the fact. So I treat it as the *target* and estimate it at runtime from
   what has been seen so far.
2. **Streams rarely end because the sender left radio range.** Receiver
   distance at a stream's last step has a median of 219 m (10th–90th
   percentile 45–314 m). The range, taken as the 99th percentile of all
   distances, is 320 m. Only 17% (validation) to 22% (test) of streams end
   within 2 s of the receiver's own recording ending. The rest end for other
   reasons: pseudonym changes, the sender leaving the simulation, or a gap in
   reception.
3. **The time left gives away the label.** 6% of validation steps are in
   one-message streams, and 98% of those are `trafficCongestionSybil`
   ghosts. The median steps left is 12 for honest senders and 6 for
   attackers. So a horizon built on the true time left would let the
   controller "know" who is a ghost. That's why it's reported only as an
   oracle upper bound.
4. **A pure geometric "time to exit range" estimate is poor here.** For
   receding senders (42% of steps) its MAE is 17.3 s, against 9.1 s for a
   constant guess. The reason is point 2.

What's implemented (`ravenx/mobility.py`, `scripts/run_horizon.py`):

- Three runtime estimators, all fitted on validation:
  - **constant**: the validation median.
  - **age**: the median time left given how many steps of the stream have
    been seen.
  - **geometric**: the time to exit range if the sender is receding,
    otherwise the age estimate.
- Each is scored on test with MAE, RMSE and bias: over all steps, split by
  label, and on steps with ≤ 10 s left.
- SVoI is replayed on test with a fixed H and with H_v(t) = min(H,
  estimated steps left). This is done for each estimator and for the
  oracle, with H ∈ {1, 2, 3, 5, 10}, both with all four evidence actions
  and with passive observation (a1) only.

## Row 16: criticality multiplier

The status document suggests "an existing event flag in the data".

1. **There is no event flag.** A NextGen CAM carries position, speed,
   acceleration, heading, driver profile (sender and receiver) and distance
   to the road edge. Nothing marks a hazard or an event.
2. **Candidate flags built from kinematics** (validation):

   | Candidate | Share of steps | Attack rate inside (outside) |
   |---|---|---|
   | distance < 30 m | 7.1% | 0.198 (0.203) |
   | distance < 50 m and closing | 5.6% | 0.131 (0.207) |
   | time to collision < 5 s | 8.5% | 0.178 (0.205) |
   | **time to collision < 10 s and distance < 100 m** | **7.6%** | **0.151 (0.207)** |
   | claimed acceleration ≤ −3 m/s² | 7.9% | 0.249 (0.199) |
   | distance < 100 m and claimed acceleration ≤ −3 m/s² | 1.6% | 0.274 (0.201) |

   I chose the bold one. It means "someone is close and closing in", it
   covers a usable share of steps, and it isn't a disguised attack
   detector: attacks are *less* common inside it. The hard-braking flags
   would partly measure the feignedBraking and suddenStop attacks
   themselves.
3. **Limitation.** The distance and closing speed come from the sender's
   claimed position, so an attacker can shape the flag. Claiming to be far
   away lowers the scrutiny they get.
4. **What the multiplier can and can't do.** Cm scales both stop costs
   (Eqs. 12–13), so the accept-vs-reject boundary p = C_FR/(C_FA+C_FR)
   doesn't move. The multiplier only changes *when* the controller stops:
   stopping gets costlier relative to evidence, so it buys more evidence on
   critical steps. A unit test checks this.
5. **Fair comparison.** For each weight W ∈ {2, 5}, the controller without
   the multiplier and the one with Cm = W on critical steps are scored on
   the same objective, where an error on a critical step costs W times more.
   The level is assumed to hold over the planning horizon: one table is
   solved per level, with no transition model between levels.

## Regression check

`run_svoi.py` was refactored to share `svoi.fit_policy`. Re-running it on the
cached beliefs reproduces `reports/svoi_hw2/svoi_results.csv` exactly
(maximum absolute difference 0.0).
