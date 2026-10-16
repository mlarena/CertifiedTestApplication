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

### Шаг 6. Детальный анализ pg_buffercache

```sql
-- Статистика по страницам в кеше
SELECT count(*) AS total_buffers,
       count(*) FILTER (WHERE relname = 't') AS t_buffers
FROM pg_buffercache b
JOIN pg_class c ON c.oid = b.relation;

-- Распределение usagecount (0 = кандидат на вытеснение, 5 = защищён)
SELECT usagecount, count(*)
FROM pg_buffercache
GROUP BY usagecount
ORDER BY usagecount;

-- Блокировка буферов для таблицы t (pin count > 0)
SELECT count(*) AS pinned_buffers
FROM pg_buffercache b
JOIN pg_class c ON c.oid = b.relation
WHERE c.relname = 't';
```

### Шаг 7. Буферное кольцо для последовательного сканирования

```sql
-- Выполняем полное сканирование
SELECT * FROM t;

-- Проверяем, какие страницы оказались в кеше
SELECT relname, count(*) AS buffers
FROM pg_buffercache b
JOIN pg_class c ON c.oid = b.relation
GROUP BY relname;

-- Пытаемся увеличить кеш для seqscan (требует прав суперпользователя)
-- ALTER SYSTEM SET seq_page_ratio = '1.0';
-- SELECT pg_reload_conf();
```

### Шаг 8. Прогрев кеша через pg_prewarm

```sql
CREATE EXTENSION pg_prewarm;

-- Прогреваем таблицу (чтение в кеш)
SELECT pg_prewarm('t');

-- Сравниваем EXPLAIN ANALYZE до и после
EXPLAIN (analyze, buffers, costs off, timing off) SELECT * FROM t;
-- Должно быть: Buffers: shared hit=443

-- Прогрев с выводом прогресса
SELECT pg_prewarm('t', 'buffer', 'page', true);

-- Прогрев индекса
SELECT pg_prewarm('idx_t', 'buffer', 'page', true);
```

### Шаг 9. Мониторинг ввода-вывода (pg_stat_io)

```sql
-- Статистика ввода-вывода (PostgreSQL 16+)
SELECT * FROM pg_stat_io WHERE context = 'normal' \gx
LIMIT 20;

-- Статистика для Vacuum
SELECT * FROM pg_stat_io WHERE context = 'vacuum' \gx
LIMIT 20;
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
