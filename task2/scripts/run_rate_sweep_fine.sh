#!/usr/bin/env bash
# Narrow the RabbitMQ degradation point between 1k and 5k msg/s at 1 KB.
# Writes to results/rate-sweep-fine.csv
set -euo pipefail

cd "$(dirname "$0")/.."

DURATION=${DURATION:-30}
PRODUCERS=${PRODUCERS:-2}
CONSUMERS=${CONSUMERS:-2}
TAG=rate-sweep-fine

for r in 2000 2500 3000 3500 4000 4500; do
    echo "=== rabbit | rate=$r | size=1024 | tag=$TAG ==="
    docker compose run --rm runner \
        --broker rabbit \
        --rate "$r" \
        --size 1024 \
        --duration "$DURATION" \
        --producers "$PRODUCERS" \
        --consumers "$CONSUMERS" \
        --tag "$TAG" \
        --out "/app/results/${TAG}.csv" || echo "run failed, continuing"
    sleep 2
done
