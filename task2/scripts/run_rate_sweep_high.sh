#!/usr/bin/env bash
# Push Redis above 10k msg/s to find its ceiling at 1 KB.
# Writes to results/rate-sweep-high.csv
set -euo pipefail

cd "$(dirname "$0")/.."

DURATION=${DURATION:-30}
PRODUCERS=${PRODUCERS:-2}
CONSUMERS=${CONSUMERS:-2}
TAG=rate-sweep-high

for r in 15000 20000 30000 50000 80000; do
    echo "=== redis | rate=$r | size=1024 | tag=$TAG ==="
    docker compose run --rm runner \
        --broker redis \
        --rate "$r" \
        --size 1024 \
        --duration "$DURATION" \
        --producers "$PRODUCERS" \
        --consumers "$CONSUMERS" \
        --tag "$TAG" \
        --out "/app/results/${TAG}.csv" || echo "run failed, continuing"
    sleep 2
done
