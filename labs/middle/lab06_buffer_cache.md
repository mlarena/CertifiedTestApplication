# Лабораторная работа №6: Буферный кеш

## Цель
Изучить устройство буферного кеша, его влияние на производительность, мониторинг через EXPLAIN ANALYZE и pg_buffercache.

## Теория
Буферный кеш — область общей памяти, в которой хранятся прочитанные с диска страницы данных. Размер настраивается параметром `shared_buffers`. При обращении к странице сначала проверяется буферный кеш, затем кеш ОС, и только потом — диск.

## Задание

### Шаг 1. Просмотр текущего размера

```sql
SHOW shared_buffers;

-- Размер кеша в байтах
SELECT setting FROM pg_settings WHERE name = 'shared_buffers';
```

### Шаг 2. Влияние буферного кеша на запрос

```sql
CREATE DATABASE lab_buffer;
\c lab_buffer

CREATE TABLE t(n integer);
INSERT INTO t SELECT id FROM generate_series(1, 100000);

-- Первый запрос (холодный кеш)
EXPLAIN (analyze, buffers, costs off, timing off)
SELECT * FROM t;

-- Второй запрос (тёплый кеш)
EXPLAIN (analyze, buffers, costs off, timing off)
SELECT * FROM t;
```

### Шаг 3. Анализ через pg_buffercache

```sql
CREATE EXTENSION pg_buffercache;

-- Количество буферов для таблицы t
SELECT count(*) AS total_buffers,
       count(*) FILTER (WHERE relfilenode = (SELECT relfilenode FROM pg_class WHERE relname = 't'))
           AS table_buffers
FROM pg_buffercache;
```

### Шаг 4. Hit ratio

```sql
-- Общая статистика hit/miss по базе данных
SELECT datname,
       blks_read,
       blks_hit,
       round(blks_hit::numeric / NULLIF(blks_hit + blks_read, 0) * 100, 2) AS hit_ratio
FROM pg_stat_database
WHERE datname = current_database();
```

### Шаг 5. Влияние размера кеша

```sql
-- Проверка параметра
SHOW shared_buffers;

-- Для сравнения: размер таблицы в страницах
SELECT pg_relation_size('t') / 8192 AS pages;
```

## Решение

### Шаг 2: Результат
```
-- Холодный кеш:
Seq Scan on t (actual rows=100000 loops=1)
  Buffers: shared read=443
Planning Time: 0.160 ms
Execution Time: 6.335 ms

-- Тёплый кеш:
Seq Scan on t (actual rows=100000 loops=1)
  Buffers: shared hit=443
Planning Time: 0.034 ms
Execution Time: 4.310 ms
```

## Контрольные вопросы

1. Что такое `shared hit` и `shared read` в EXPLAIN ANALYZE?
2. Почему второй запрос быстрее первого?
3. Как увеличить `shared_buffers` и когда это нужно?

## Дополнительное задание

Измерьте время выполнения запроса при `shared_buffers = 128MB` и при `shared_buffers = 1GB` (потребуется перезапуск сервера).
