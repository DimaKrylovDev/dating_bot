#!/usr/bin/env bash
# Helper: runs all 3 workloads for ONE strategy.
# Usage: bash scripts/_run_strategy.sh <strategy> [duration] [workers] [keys]
set -euo pipefail

cd "$(dirname "$0")/.."

STRATEGY="${1:?strategy required}"
DURATION="${2:-20}"
WORKERS="${3:-16}"
KEYS="${4:-1000}"
OUT="results/results-${STRATEGY}.csv"

rm -f "$OUT"

WORKLOADS=(
  "read_heavy:0.8"
  "balanced:0.5"
  "write_heavy:0.2"
)

echo
echo "############################################################"
echo "# strategy: $STRATEGY"
echo "# duration=${DURATION}s  workers=${WORKERS}  keys=${KEYS}"
echo "############################################################"

echo "== bringing up infra =="
docker compose up -d postgres redis
echo "== building runner image =="
docker compose build runner

for w in "${WORKLOADS[@]}"; do
  label="${w%%:*}"
  ratio="${w##*:}"
  echo
  echo "===> [$STRATEGY] workload=$label ratio=$ratio"
  docker compose run --rm runner \
    --strategy "$STRATEGY" \
    --read-ratio "$ratio" \
    --duration "$DURATION" \
    --workers "$WORKERS" \
    --keys "$KEYS" \
    --label "$label" \
    --out "/app/$OUT"
done

echo
echo "== done [$STRATEGY]. results in $OUT =="
column -s, -t < "$OUT"
