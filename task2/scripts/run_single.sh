#!/usr/bin/env bash
# Run one benchmark inside the runner container.
# Usage: scripts/run_single.sh <broker> <rate> <size> <duration> [producers] [consumers] [tag]
# Output file is derived from the tag: results/<tag>.csv
set -euo pipefail

BROKER=${1:?broker (rabbit|redis)}
RATE=${2:?rate msg/sec}
SIZE=${3:?size bytes}
DURATION=${4:?duration seconds}
PRODUCERS=${5:-1}
CONSUMERS=${6:-1}
TAG=${7:-manual}

docker compose run --rm runner \
    --broker "$BROKER" \
    --rate "$RATE" \
    --size "$SIZE" \
    --duration "$DURATION" \
    --producers "$PRODUCERS" \
    --consumers "$CONSUMERS" \
    --tag "$TAG" \
    --out "/app/results/${TAG}.csv"
