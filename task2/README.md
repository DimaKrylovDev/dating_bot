# task2 — RabbitMQ vs Redis benchmark

Identical producer/consumer stand, identical message format, switchable broker.
Python + asyncio. Brokers run as separate containers with capped CPU/RAM so a
single instance can actually be stressed on a laptop.

## Layout

- `src/brokers/` — `Broker` abstraction + RabbitMQ (`aio-pika`) and Redis
  (`redis.asyncio`, LPUSH/BRPOP on a list) implementations.
- `src/producer.py` — async rate-paced producer.
- `src/consumer.py` — async consumer, measures per-message latency
  (`recv_time - send_time` from the embedded message timestamp).
- `src/runner.py` — CLI that wires one run, drains the queue, appends a row to
  `results/results.csv`.
- `scripts/run_matrix.sh` — runs the full experiment matrix.
- `results/report.md` — methodology + table to fill in + conclusions.

## Prerequisites

- Docker + Docker Compose.
- Both brokers run with `cpus=1.0, mem=1g` — this is what lets you see a
  single instance degrade at realistic laptop rates. Adjust in
  [docker-compose.yml](docker-compose.yml) if you want a different ceiling.

## Run it

```bash
# 1. start brokers
docker compose up -d rabbitmq redis

# 2. build runner image once
docker compose build runner

# 3. full matrix (takes ~15 min at defaults)
./scripts/run_matrix.sh

# narrow the RabbitMQ degradation point between 1k and 5k msg/s
./scripts/run_rate_sweep_fine.sh

# push Redis above 10k to find its ceiling
./scripts/run_rate_sweep_high.sh

# ...or a single experiment (output → results/<tag>.csv)
./scripts/run_single.sh rabbit 5000 1024 30 2 2 baseline
./scripts/run_single.sh redis  5000 1024 30 2 2 baseline
```

Each experiment appends to its own file under `results/`, named after the tag:

| Tag              | File                              | What it holds                              |
|------------------|-----------------------------------|--------------------------------------------|
| `baseline`       | `results/baseline.csv`            | Experiment 1 — equal load on both brokers  |
| `size-sweep`     | `results/size-sweep.csv`          | Experiment 2 — 128B / 1KB / 10KB / 100KB   |
| `rate-sweep`     | `results/rate-sweep.csv`          | Experiment 3 — 1k / 5k / 10k msg/s         |
| `rate-sweep-fine`| `results/rate-sweep-fine.csv`     | Narrow RabbitMQ breaking point             |
| `rate-sweep-high`| `results/rate-sweep-high.csv`     | Push Redis above 10k                       |
| `smoke` / `manual` | `results/smoke.csv` etc.        | Ad-hoc runs                                |

Each row has target vs. achieved rate, sent/received counts, latency
percentiles, final backlog, and errors.

## Runner CLI

```
python -m src.runner \
    --broker {rabbit|redis} \
    --rate <target msg/sec> \
    --size <bytes> \
    --duration <producer seconds> \
    --producers N --consumers N \
    [--drain-timeout 30] [--tag label] \
    [--out /app/results/<tag>.csv]
```

Notes:

- `--rate` is total target msg/s across all producers; each producer aims for
  `rate / producers`.
- After producers stop, the runner waits up to `--drain-timeout` for consumers
  to clear the queue. Whatever is still in the queue is recorded as
  `final_backlog` — that is the signal that a broker could not keep up with the
  offered load.
- Messages are JSON with `{"s": seq, "t": send_ts, "p": "xxxx..."}` padded
  to the requested byte size. Non-persistent delivery on both sides.
- Latency is `recv_wall_time − send_wall_time`; since producer and consumer run
  in the same process, there's no clock skew.

## What the experiments cover

The matrix in [scripts/run_matrix.sh](scripts/run_matrix.sh) runs the three
experiments required:

1. **Baseline** — identical load (5 000 msg/s, 1 KB, 30 s) on both brokers.
2. **Size sweep** — 128 B / 1 KB / 10 KB / 100 KB at a moderate 2 000 msg/s.
3. **Rate sweep** — 1 000 / 5 000 / 10 000 msg/s at a fixed 1 KB payload.

After runs finish, inspect the per-experiment CSV files in `results/` and fill
in [results/report.md](results/report.md) with the observed numbers and the
breakdown points.

## Observing broker resource usage

While a run is in progress, in another terminal:

```bash
docker stats bench-rabbit bench-redis
# RabbitMQ management UI (queue depth, publish/deliver rate):
open http://localhost:15672   # guest / guest
```

Use these for the CPU / RAM / backlog columns in the report.
