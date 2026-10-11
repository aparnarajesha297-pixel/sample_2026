# Threshold re-tuning on target data: reading the results

Numbers are in `report.md` next to this file. Phase 1 covers the five tests whose source is not highway_7 (3 seeds, all models). The two highway_7-source pairs are added by phase 2.

Checks before reading anything: all 63 retrained models give exactly the F1 of the earlier cross-scenario run (`reports/cross_scenario_19f`), and the saved scores reproduce each run's own F1 (`score_check.csv`). The tuned threshold never sees the receivers it is scored on.

## What re-tuning fixes

Most of the cross-domain F1 collapse of the neural models was a threshold problem. Re-picking the threshold on a handful of labelled target receivers recovers it:

- Low → High density, RAVEN-X-GF: 0.612 → 0.801 with 1% of target receivers labelled (one file per attack run, 15 files). GRU goes 0.495 → 0.748, GAT 0.582 → 0.714.
- urban_2 → highway_7, RAVEN-X-GF: 0.640 → 0.783 at 1%.
- Urban → Highway, RAVEN-X-GF: 0.699 → 0.779 at 1%.

The 1% budget already gets within about 0.01 of the oracle threshold almost everywhere, and going to 20% adds very little. The spread from which receivers end up in the slice is small too (F1 std over draws about 0.008).

The tree models barely move (+0.000 to +0.02). Their source thresholds were already close to right, which fits the earlier picture: the trees' scores keep their meaning across domains, the neural models' scores shift.

The highway-trained and urban_2 → highway_2 tests gain under 0.01 for every model, because there was little to recover. On urban_2 → highway_2 the 1% budget is slightly worse than the source threshold (−0.001); that's slice noise on a test where the source threshold was already near optimal.

## What it does not fix

Re-tuning repairs the threshold, not the ranking. Where the neural model's PR-AUC dropped, the oracle threshold is a ceiling it cannot get past:

- Urban → Highway: RAVEN-X-GF's oracle F1 is 0.788, still below Random Forest (0.857) and XGBoost (0.847) after they are re-tuned too.
- urban_2 → highway_7: RAVEN-X-GF 0.790 against XGBoost 0.840.
- Low → High density is the one test where RAVEN-X-GF moves into the lead among neural models and close to the trees: 0.807 against Random Forest 0.831 and XGBoost 0.783.

The seed instability is also only partly gone. The source-threshold F1 of RAVEN-X-GF on urban_2 → highway_7 was 0.764 / 0.481 / 0.675 over seeds 0-2; after re-tuning it is 0.826 / 0.749 / 0.795. Seed 1 is still the weak one because its ranking is worse (oracle 0.752), not just its threshold. Same for Low → High seed 2 (oracle 0.754 vs 0.83 for the other two).

## Caveats

- highway_7 has only 15 receiver files per attack run, so the 1% and 5% budgets both mean one file per run there; the slice is still large in steps (about 90-100k) because highway_7 logs are long.
- The label budget counts receiver files, not steps. One urban receiver file is much shorter than a highway_7 one, so "1%" means different amounts of labelling effort per target.
- Labelling a few receiver logs in a new environment is a real cost. It's a deployment-time calibration step, not something the detector does on its own.

## Bottom line

For the paper, the fair cross-domain claim for RAVEN-X-GF is "with a small target calibration set". Without it, the urban-trained and low-density-trained neural models are unreliable. With it, RAVEN-X-GF is competitive on density shift, and still behind the tree models when moving from urban to highway roads.
