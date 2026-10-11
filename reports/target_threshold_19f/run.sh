#!/bin/bash
# Threshold re-tuning on target data: re-run cross-scenario with saved scores.
# Phase 1 = tests whose source is not highway_7 (fast), phase 2 = highway_7 sources.
cd /home/user/sample_2026
COMMON="--data nextgen --root /home/user/data/nextgen --density-map highway_2=low,highway_7=high --quiet"
for s in 0 1 2; do
  echo "=== p1 seed $s start $(date +%m-%d\ %H:%M) ==="
  python3 scripts/run_cross_scenario.py $COMMON --seeds $s --out results/cross_tt/seed_$s --save-scores results/cross_tt/seed_$s/scores \
    --tests "Urban → Highway" "Low → High density" "highway_2 → urban_2" "urban_2 → highway_2" "urban_2 → highway_7" \
    >> results/cross_tt/seed_$s.log 2>&1 && echo "=== p1 seed $s done $(date +%m-%d\ %H:%M) ===" || { echo FAILED; exit 1; }
done
python3 scripts/run_target_threshold.py results/cross_tt/seed_0 results/cross_tt/seed_1 results/cross_tt/seed_2 \
  --out reports/target_threshold_19f > results/cross_tt/analysis.log 2>&1 && echo "=== PHASE1_ANALYSED ===" || echo "=== analysis FAILED ==="
for s in 0 1 2; do
  echo "=== p2 seed $s start $(date +%m-%d\ %H:%M) ==="
  python3 scripts/run_cross_scenario.py $COMMON --seeds $s --out results/cross_tt/seed_$s --save-scores results/cross_tt/seed_$s/scores \
    --tests "highway_7 → highway_2" "highway_7 → urban_2" \
    >> results/cross_tt/seed_$s.log 2>&1 && echo "=== p2 seed $s done $(date +%m-%d\ %H:%M) ===" || { echo FAILED; exit 1; }
done
python3 scripts/run_target_threshold.py results/cross_tt/seed_0 results/cross_tt/seed_1 results/cross_tt/seed_2 \
  --out reports/target_threshold_19f > results/cross_tt/analysis.log 2>&1 && echo "=== analysed ===" || echo "=== analysis FAILED ==="
echo TT_DONE
