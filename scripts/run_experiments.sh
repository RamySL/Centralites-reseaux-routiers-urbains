#!/usr/bin/env bash
# Lance toutes les expériences depuis la racine du dépôt.
# Les options sont transmises à scripts/figure2.py, par exemple :
#   ./scripts/run_experiments.sh --centralities straightness closeness
#   ./scripts/run_experiments.sh --cities Rome Chicago --recompute
# Liste complète des options : ./scripts/run_experiments.sh --help
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH=src
PYTHON="${PYTHON:-python3}"

"$PYTHON" scripts/figure2.py "$@"
