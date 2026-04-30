#!/usr/bin/env bash
# Runs all 3 workloads for the cache-aside strategy.
# Usage: bash scripts/run_cache_aside.sh [duration] [workers] [keys]
set -euo pipefail
cd "$(dirname "$0")/.."
exec bash scripts/_run_strategy.sh cache_aside "$@"
