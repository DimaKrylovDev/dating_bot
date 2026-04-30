# task3 — сравнение стратегий кеширования

Три варианта одной KV-системы (Postgres + Redis), отличающиеся только стратегией работы с кешем:

| стратегия      | чтение                                  | запись                                  |
|----------------|-----------------------------------------|-----------------------------------------|
| `cache_aside`  | cache → DB при miss → положить в cache  | прямо в БД, ключ удаляется из кеша      |
| `write_through`| cache → DB при miss → положить в cache  | синхронно в cache **и** в DB            |
| `write_back`   | cache → DB при miss → положить в cache  | в cache; фоновый воркер батчами в DB    |

## Состав

- `src/db.py` — обёртка Postgres со счётчиком обращений.
- `src/cache.py` — обёртка Redis со счётчиком hit/miss.
- `src/app.py` — три стратегии (общий интерфейс `get` / `set` / `stop`).
- `src/load.py` — самописный нагрузочный генератор (потоки, заданная длительность, ratio R/W).
- `src/runner.py` — CLI: настраивает БД и кеш, гоняет нагрузку, пишет CSV.
- `scripts/run_all.sh` — гонит все 3×3 матрицу.
- `docker-compose.yml` — Postgres 16 + Redis 7 + runner-контейнер с профилем `tools`.

## Запуск

```bash
cd task3

# полный матричный прогон (по умолчанию: 20с, 16 воркеров, 1000 ключей)
bash scripts/run_all.sh

# или один сценарий вручную:
docker compose up -d postgres redis
docker compose build runner
docker compose run --rm runner \
  --strategy write_back \
  --read-ratio 0.2 \
  --duration 20 \
  --workers 16 \
  --keys 1000 \
  --label write_heavy \
  --out /app/results/results.csv
```

Результаты — в [results/results.csv](results/results.csv); итоговый отчёт — в
[results/report.md](results/report.md).

## Метрики, которые пишутся в CSV

- `throughput_rps` — общая пропускная способность,
- `avg_latency_ms`, `p50_ms`, `p95_ms`, `p99_ms` — латентности операций,
- `db_reads`, `db_writes` — реальные обращения в Postgres,
- `cache_hits`, `cache_misses`, `hit_rate` — статистика Redis,
- `wb_max_queue`, `wb_flush_batches`, `wb_flush_rows`, `wb_pending_at_end` — для
  write-back показывают, как накапливалась очередь и сколько строк добивал
  фоновый flusher,
- `stop_drain_s` — время, потраченное на финальный сброс write-back-очереди в
  БД при остановке (для остальных стратегий ≈ 0).
