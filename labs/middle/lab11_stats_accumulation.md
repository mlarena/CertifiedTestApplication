# Лабораторная работа №11: Накопительная статистика

## Цель
Изучить систему накопительной статистики PostgreSQL: pg_stat_all_tables, pg_statio, pg_stat_database, pg_stat_io.

## Теория
PostgreSQL собирает статистику по обращениям к таблицам, индексам и общую статистику базы данных. Данные хранятся в разделяемой памяти и записываются в `PGDATA/pg_stat/` при штатной остановке. Уровень кеширования настраивается через `stats_fetch_consistency`.

## Задание

### Шаг 1. Сброс статистики

```sql
CREATE DATABASE lab_stats;
\c lab_stats

SELECT pg_stat_reset();
SELECT pg_stat_reset_shared('io');
```

### Шаг 2. Создание нагрузки

```bash
pgbench -i lab_stats
pgbench -T 10 lab_stats
```

### Шаг 3. Статистика по таблицам (строки)

```sql
SELECT relname, seq_scan, idx_scan, n_tup_ins, n_tup_upd, n_tup_del,
       n_live_tup, n_dead_tup
FROM pg_stat_all_tables
WHERE schemaname = 'public';
```

### Шаг 4. Статистика по таблицам (страницы)

```sql
SELECT relname, heap_blks_read, heap_blks_hit,
       idx_blks_read, idx_blks_hit
FROM pg_statio_all_tables
WHERE schemaname = 'public';
```

### Шаг 5. Статистика по индексам

```sql
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_all_indexes
WHERE relname = 'pgbench_accounts';
```

### Шаг 6. Общая статистика БД

```sql
SELECT datname, numbackends, xact_commit, xact_rollback,
       blks_read, blks_hit,
       tup_returned, tup_fetched, tup_inserted, tup_updated,
       deadlocks, temp_files, temp_bytes
FROM pg_stat_database
WHERE datname = 'lab_stats';
```

### Шаг 7. Статистика ввода-вывода

```sql
SELECT backend_type, sum(hits) hits, sum(reads) reads, sum(writes) writes
FROM pg_stat_io
GROUP BY backend_type;
```

## Решение

### Шаг 3: Результат
```
    relname    | seq_scan | idx_scan | n_tup_ins | n_tup_upd | n_tup_del | n_live_tup | n_dead_tup
---------------+----------+----------+-----------+-----------+-----------+------------+------------
 pgbench_accounts |      0 |     2720 |         0 |      1360 |         0 |          0 |       1248
 pgbench_branches |      0 |      136 |         0 |       136 |         0 |         32 |          0
 pgbench_tellers  |      0 |      272 |         0 |       272 |         0 |        100 |          0
(3 rows)
```

## Контрольные вопросы

1. Что показывает `n_dead_tup` и почему оно растёт?
2. Как найти неиспользуемые индексы по статистике?
3. Какой параметр включает мониторинг времени ввода-вывода?

## Дополнительное задание

С помощью `pg_stat_activity` и `pg_locks` определите, какая таблица блокирует longest-running транзакцию.
