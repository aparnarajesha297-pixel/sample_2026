# Verification of the "SVoI Controller & RS-WeightedTrim" guide

## Part 2: RS-WeightedTrim — verified and implemented

The two-stage recipe is internally consistent and implementable as written.
It is in `ravenx/federated.py`, with tests in `tests/test_pipeline.py`:

- **Stage 1** (`capped_simplex_projection`): water-filling. Weights sum to 1,
  and no weight exceeds kappa/n, on 300 random heavy-tailed cases. It matches
  a direct port of the guide's reference loop to 1e-12.
- **Stage 2** (`weighted_trimmed_mean`): per coordinate, trims ceil(beta_trim·n)
  from each end, then averages the survivors with their Stage-1 weights,
  renormalised over the survivors only. It matches the guide's reference
  aggregate. An extreme RSU with the largest raw score is trimmed out.
- Order: weights are capped first, then trimmed. Aggregating updates (deltas)
  instead of parameters gives the identical model, because every RSU starts
  from the same global parameters.
- Choices made: raw trust score W^_i = reputation_i × n_i (reputation = moving
  average of max(0, cosine to the median update)), kappa = 2, beta_trim = 0.2.
  With n = 20 and f = 4 compromised RSUs, 4 values are trimmed per side and
  12 survive.
- The old rule is kept as the `ReputationDrop` baseline. Theorem 1 does not
  cover it.

Two points to align in the paper:

1. **Wording of "projection".** The guide's water-filling rescales the
   uncapped weights in proportion. That is not the Euclidean projection onto
   the capped simplex, which shifts all uncapped weights by the same
   constant. Both give valid weights (sum 1, each ≤ kappa/n), so a bound that
   uses only those two properties holds either way. But if the paper defines
   Π as the Euclidean projection, the text and the code describe different
   operators.
2. **Zero-score edge case.** If every uncapped RSU has raw score 0, the
   guide's loop divides by zero. The implementation shares the excess
   equally among them, so the weights still sum to 1.

## Part 1: SVoI controller (Eqs. 12–17) — not implemented yet; issues to settle first

The recursion (Eqs. 14–17) and Algorithm 1 are standard finite-horizon dynamic
programming and are fine. The problems are in the numbers and modelling
choices around it. As written, several of them would make the controller
degenerate: its results would look fine but mean nothing.

1. **Cost scale: the example values make evidence never worth buying.**
   C_stop = min(C_FA·p, C_FR·(1−p)) is largest at p = C_FR/(C_FA+C_FR), where it
   equals C_FA·C_FR/(C_FA+C_FR). With the guide's C_FA = 5, C_FR = 1 that is
   0.83 (checked numerically). Even the cheapest evidence action costs 1, so
   Q ≥ 1 > C_stop everywhere: the controller always stops at once and reduces to
   a fixed threshold. Requirement: C̄·C_FA·C_FR/(C_FA+C_FR) > Cost(a₁).
   Proposal: keep the 5:1 ratio at a larger scale, e.g. C_FA = 100, C_FR = 20
   (maximum stopping cost 16.7).
2. **Actions a₂–a₄ modelled as "reduce uncertainty by a fixed amount" have
   zero value.** C_stop depends only on p(b). If an action changes
   uncertainty but not risk, C_stop(b′) = C_stop(b), so a₂–a₄ only add cost
   and are never chosen. Proposal: model each evidence action as an extra
   noisy check of the true state with reliability ρ_a (for example
   ρ = 0.80 / 0.90 / 0.99 for a₂ / a₃ / a₄). p then updates by Bayes' rule, the
   two outcomes occur with probabilities implied by p, and uncertainty
   shrinks. This gives real value of information and needs no test labels.
   It is still an assumption and must be stated as one.
3. **γ < 1 rewards postponing decisions.** Because costs are minimised,
   discounting makes a later wrong decision look cheaper than the same one
   now, so waiting is favoured for no real reason. Proposal: γ = 1 (the
   finite horizon H already keeps V finite), or discount only the evidence
   costs.
4. **Where a₁ transitions come from.** Beliefs are model outputs (risk,
   uncertainty), so passive transitions must be counted from the model's
   predictions on consecutive steps of the same stream, not from
   `sequence_dataset.pkl` (raw features). Estimate them on the **validation**
   split: on training data the model is over-confident, which makes
   transitions look better than they are. Test data is never used.
5. **Belief grid.** Real uncertainty values lie roughly between 0.02 and 0.3,
   so a uniform 20×20 grid over [0,1]² leaves most cells empty. Proposal:
   quantile bins fitted on validation beliefs.
6. **p(b) per cell.** Use the temperature-scaled probability at the cell
   (calibration fitted on validation), or the empirical attack rate in the
   cell on validation.
7. **Criticality C̄_m(c).** There is no criticality head yet (row 16), and
   NextGen has no event or criticality flag. Until one exists, K = 1 and C̄ = 1.
8. **The H = 1 "correctness check" can't catch much.** At h = 1 the
   recursion is literally the one-step rule, so the check only catches
   indexing mistakes. Stronger check: compare the table against a brute-force
   expectimax search on a small grid for H = 2 and 3.
9. **Store accept vs. reject.** The guide's pseudo-code merges them into one
   "accept_or_reject" entry. The policy table must record which one is
   cheaper.
10. **Runtime horizon H_v(t)** depends on the mobility model (row 15). Until
    then, use a fixed H (for example 1, 2, 3, 5) and report each value.
