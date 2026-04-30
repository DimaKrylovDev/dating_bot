#!/usr/bin/env bash
# Runs all 3 strategies x 3 workloads, appends rows into results/results.csv
# Usage:  bash scripts/run_all.sh [duration_seconds] [workers] [keys]
set -euo pipefail

cd "$(dirname "$0")/.."

DURATION="${1:-20}"
WORKERS="${2:-16}"
KEYS="${3:-1000}"
OUT="results/results.csv"

# fresh CSV
rm -f "$OUT"

STRATS=(cache_aside write_through write_back)
# label, read_ratio
WORKLOADS=(
  "read_heavy:0.8"
  "balanced:0.5"
  "write_heavy:0.2"
)

echo "== bringing up infra =="
docker compose up -d postgres redis
echo "== building runner image =="
docker compose build runner

for s in "${STRATS[@]}"; do
  for w in "${WORKLOADS[@]}"; do
    label="${w%%:*}"
    ratio="${w##*:}"
    echo
    echo "===> strategy=$s workload=$label ratio=$ratio"
    docker compose run --rm runner \
      --strategy "$s" \
      --read-ratio "$ratio" \
      --duration "$DURATION" \
      --workers "$WORKERS" \
      --keys "$KEYS" \
      --label "$label" \
      --out "/app/$OUT"
  done
done

echo
echo "== done. results in $OUT =="
column -s, -t < "$OUT" | head -n 40 || true
