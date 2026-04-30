#!/usr/bin/env bash
# Runs all 3 workloads for the write-back strategy.
# Usage: bash scripts/run_write_back.sh [duration] [workers] [keys]
set -euo pipefail
cd "$(dirname "$0")/.."
exec bash scripts/_run_strategy.sh write_back "$@"
