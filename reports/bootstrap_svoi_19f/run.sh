#!/bin/bash
cd /home/user/sample_2026
D="--data nextgen --root /home/user/data/nextgen/hw2"; B="--beliefs results/svoi_hw2_nbr/beliefs.npz"
nice -n 10 python3 scripts/run_bootstrap_costs.py $D $B --out results/bootstrap_svoi_19f > results/bootstrap_svoi_19f.log 2>&1 && echo "=== active done $(date +%H:%M) ===" || echo "=== active FAILED ==="
nice -n 10 python3 scripts/run_bootstrap_costs.py $D $B --evidence a1 --out results/bootstrap_svoi_19f_passive > results/bootstrap_svoi_19f_passive.log 2>&1 && echo "=== passive done $(date +%H:%M) ===" || echo "=== passive FAILED ==="
echo BOOT_DONE
