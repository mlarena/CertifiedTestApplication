# Лабораторная работа №15: Параллельные запросы

## Цель
Изучить механизм параллельного выполнения запросов: параметры настройки, типы операторов, влияние на производительность.

## Теория
PostgreSQL поддерживает параллельное выполнение: Seq Scan, Hash Join, Merge Join, Aggregate. Количество воркеров настраивается через `max_parallel_workers_per_gather`, `max_parallel_workers`, `max_worker_processes`.

## Задание

### Шаг 1. Проверка параметров

```sql
SHOW max_parallel_workers_per_gather;
SHOW max_parallel_workers;
SHOW max_worker_processes;
SHOW parallel_tuple_cost;
SHOW min_parallel_table_scan_size;
```

### Шаг 2. Параллельный Seq Scan

```sql
CREATE DATABASE lab_parallel;
\c lab_parallel

CREATE TABLE t AS
SELECT id, md5(id::text) AS data
FROM generate_series(1, 10000000) AS id;
ANALYZE t;

-- Без параллелизма
SET max_parallel_workers_per_gather = 0;
EXPLAIN (analyze, costs off)
SELECT count(*) FROM t;

-- С параллелизмом
SET max_parallel_workers_per_gather = 4;
EXPLAIN (analyze, costs off)
SELECT count(*) FROM t;
```

### Шаг 3. Параллельный Hash Join

```sql
CREATE TABLE t2 AS SELECT * FROM t WHERE id % 100 = 0;
ANALYZE t2;

SET max_parallel_workers_per_gather = 4;
EXPLAIN (analyze, costs off)
SELECT count(*) FROM t JOIN t2 ON t.data = t2.data;
```

### Шаг 4. Влияние min_parallel_table_scan_size

```sql
-- Маленькая таблица
CREATE TABLE small_t AS SELECT * FROM t WHERE id < 1000;
ANALYZE small_t;

SET min_parallel_table_scan_size = '8MB';
EXPLAIN (analyze, costs off)
SELECT count(*) FROM small_t;

SET min_parallel_table_scan_size = '8kB';
EXPLAIN (analyze, costs off)
SELECT count(*) FROM small_t;
```

### Шаг 5. Параллельная сортировка

```sql
SET max_parallel_workers_per_gather = 4;
EXPLAIN (analyze, costs off)
SELECT * FROM t ORDER BY data LIMIT 1000;
```

## Решение

### Шаг 2: Результат
```
-- Без параллелизма:
Aggregate  (actual rows=1 loops=1)
  ->  Seq Scan on t  (actual rows=10000000 loops=1)
  Buffers: shared hit=44320
Execution Time: 1200.000 ms

-- С параллелизмом:
Finalize Aggregate  (actual rows=1 loops=1)
  ->  Gather  (actual rows=1 loops=3)
        Workers Planned: 3
        Workers Launched: 3
        ->  Partial Aggregate  (actual rows=1 loops=4)
              ->  Parallel Seq Scan on t  (actual rows=2500000 loops=4)
Execution Time: 400.000 ms
```

## Контрольные вопросы

1. Почему `max_parallel_workers_per_gather` не должен превышать количество ядер?
2. Как параллелизм влияет на `work_mem`?
3. Какие типы запросов НЕ могут быть параллельными?

## Дополнительное задание

Измерьте ускорение для запросов `SELECT count(*)`, `SELECT * ORDER BY` и `JOIN` при 1, 2 и 4 воркерах.
