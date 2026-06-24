# Лабораторная работа №13: work_mem и производительность

## Цель
Изучить влияние параметров `work_mem` и `maintenance_work_mem` на производительность сортировок, хеш-соединений и операций обслуживания.

## Теория
`work_mem` — объём памяти для операций сортировки и хеш-соединений одного запроса. Недостаточное значение приводит к использованию диска (temp files). `maintenance_work_mem` — память для VACUUM, CREATE INDEX, ALTER TABLE.

## Задание

### Шаг 1. Создание нагрузки

```sql
CREATE DATABASE lab_workmem;
\c lab_workmem

CREATE TABLE big_table AS
SELECT id, md5(id::text) AS data
FROM generate_series(1, 1000000) AS id;

CREATE INDEX idx_big ON big_table(data);
ANALYZE big_table;
```

### Шаг 2. Наблюдение за temp файлами

```sql
-- Сброс
ALTER SYSTEM SET work_mem = '4MB';
SELECT pg_reload_conf();

-- Запрос с сортировкой
EXPLAIN (analyze, costs off)
SELECT * FROM big_table ORDER BY data LIMIT 100;

-- Проверяем temp файлы
SELECT temp_blks_written FROM pg_stat_database
WHERE datname = 'lab_workmem';
```

### Шаг 3. Увеличение work_mem

```sql
ALTER SYSTEM SET work_mem = '64MB';
SELECT pg_reload_conf();

EXPLAIN (analyze, costs off)
SELECT * FROM big_table ORDER BY data LIMIT 100;

-- Сравниваем время и temp файлы
```

### Шаг 4. Влияние на хеш-соединения

```sql
CREATE TABLE t2 AS SELECT * FROM big_table WHERE id % 10 = 0;
ANALYZE t2;

-- Хеш-соединение с маленьким work_mem
ALTER SYSTEM SET work_mem = '4MB';
SELECT pg_reload_conf();

EXPLAIN (analyze, costs off)
SELECT count(*) FROM big_table b JOIN t2 ON b.data = t2.data;

-- С большим work_mem
ALTER SYSTEM SET work_mem = '256MB';
SELECT pg_reload_conf();

EXPLAIN (analyze, costs off)
SELECT count(*) FROM big_table b JOIN t2 ON b.data = t2.data;
```

### Шаг 5. maintenance_work_mem

```sql
SHOW maintenance_work_mem;

-- Сравнение времени CREATE INDEX
ALTER SYSTEM SET maintenance_work_mem = '128MB';
SELECT pg_reload_conf();

\timing on
DROP INDEX IF EXISTS idx_big;
CREATE INDEX idx_big ON big_table(data);
```

## Решение

### Шаг 2: Результат (work_mem = 4MB)
```
Sort  (actual rows=100 loops=1)
  Sort Method: external merge  Disk: 12000kB
Buffers: shared hit=2840 read=1600
Execution Time: 120.456 ms
```

### Шаг 3: Результат (work_mem = 64MB)
```
Sort  (actual rows=100 loops=1)
  Sort Method: quicksort  Memory: 4096kB
Buffers: shared hit=4440
Execution Time: 85.123 ms
```

## Контрольные вопросы

1. Почему `work_mem` задаётся на уровне запроса, а не сеанса?
2. Как `maintenance_work_mem` влияет на VACUUM FULL?
3. Каковы рекомендуемые значения для сервера с 64 ГБ RAM?

## Дополнительное задание

Измерьте производительность запроса `ORDER BY` при `work_mem = 1MB`, `16MB`, `128MB`, `1GB`. Постройте таблицу результатов.
