#!/usr/bin/env bash
# Run full experiment matrix for both brokers.
# Each experiment writes to its own CSV: results/<tag>.csv.
# Requires stack to be up: `docker compose up -d rabbitmq redis`.
set -euo pipefail

cd "$(dirname "$0")/.."

SIZES=(128 1024 10240 102400)            # 128B, 1KB, 10KB, 100KB
RATES=(1000 5000 10000)                  # msg/sec
DURATION=${DURATION:-30}
PRODUCERS=${PRODUCERS:-2}
CONSUMERS=${CONSUMERS:-2}

mkdir -p results

run () {
    local broker=$1 rate=$2 size=$3 tag=$4
    echo "=== $broker | rate=$rate | size=${size}B | tag=$tag ==="
    docker compose run --rm runner \
        --broker "$broker" \
        --rate "$rate" \
        --size "$size" \
        --duration "$DURATION" \
        --producers "$PRODUCERS" \
        --consumers "$CONSUMERS" \
        --tag "$tag" \
        --out "/app/results/${tag}.csv" || echo "run failed, continuing"
    sleep 2
}

# Experiment 1 — baseline (→ results/baseline.csv)
for broker in rabbit redis; do
    run "$broker" 5000 1024 baseline
done

# Experiment 2 — message size sweep (→ results/size-sweep.csv)
for broker in rabbit redis; do
    for size in "${SIZES[@]}"; do
        run "$broker" 2000 "$size" size-sweep
    done
done

# Experiment 3 — intensity sweep (→ results/rate-sweep.csv)
for broker in rabbit redis; do
    for rate in "${RATES[@]}"; do
        run "$broker" "$rate" 1024 rate-sweep
    done
done

echo "Done. See results/baseline.csv, results/size-sweep.csv, results/rate-sweep.csv"
