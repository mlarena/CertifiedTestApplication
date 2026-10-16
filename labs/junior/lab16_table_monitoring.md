# Лабораторная работа №16: Мониторинг таблиц

## Цель
Научиться отслеживать состояние таблиц: счётчики изменений, мёртвые версии, автоочистку, активность запросов через `pg_stat_user_tables` и `pg_stat_activity`.

## Теория
PostgreSQL накапливает статистику по каждой таблице: количество вставок, обновлений, удалений, мёртвых версий,Last vacuum/analyze. Эти данные доступны через представления `pg_stat_user_tables` и `pg_stat_all_tables`.

`pg_stat_activity` показывает текущие запросы и состояние сеансов — полезно для диагностики блокировок и долгих операций.

## Задание

### Шаг 1. Счётчики изменений таблицы

```sql
CREATE DATABASE lab_monitoring;
\c lab_monitoring

CREATE TABLE t(id integer PRIMARY KEY, val text);
INSERT INTO t SELECT generate_series(1, 1000), md5(random()::text);

-- Текущая статистика
SELECT relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
WHERE relname = 't';
```

### Шаг 2. Наблюдение за mёртвыми версиями

```sql
-- Обновляем половину строк
UPDATE t SET val = 'updated' WHERE id % 2 = 0;

-- Смотрим счётчики
SELECT relname, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
FROM pg_stat_user_tables
WHERE relname = 't';
```

### Шаг 3. Автоочистка таблицы

```sql
-- Последний vacuum/analyze
SELECT relname, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 't';

-- Порог запуска автоочистки
SELECT relname, n_dead_tup, autovacuum_threshold, autovacuum_threshold + 50 AS threshold
FROM pg_stat_user_tables
WHERE relname = 't';
```

### Шаг 4. Статистика индексов

```sql
CREATE INDEX idx_t_val ON t(val);

-- Сканирование индекса
SELECT relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 't';
```

### Шаг 5. Текущие запросы через pg_stat_activity

```sql
-- Все активные запросы
SELECT pid, usename, state, query, wait_event_type, wait_event, query_start
FROM pg_stat_activity
WHERE state != 'idle';

-- Долгие запросы (дольше 1 секунды)
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE now() - query_start > interval '1 second'
  AND state = 'active';
```

### Шаг 6. Диагностика блокировок

```sql
-- pg_stat_activity с блокировками
SELECT a.pid, a.state, a.query, a.wait_event_type, a.wait_event,
       pg_blocking_pids(a.pid) AS blocked_by
FROM pg_stat_activity a
WHERE cardinality(pg_blocking_pids(a.pid)) > 0;

-- pg_locks
SELECT locktype, relation::regclass, mode, granted, pid
FROM pg_locks
WHERE NOT granted;
```

### Шаг 7. Полный мониторинг

```sql
-- Таблица с полной статистикой
SELECT
    relname,
    seq_scan, seq_tup_read,
    idx_scan, idx_tup_fetch,
    n_tup_ins, n_tup_upd, n_tup_del,
    n_live_tup, n_dead_tup,
    round(n_dead_tup::numeric / nullif(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct,
    last_vacuum, last_autovacuum,
    last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 't';
```

## Решение

### Шаг 2: Результат
```
 relname | n_tup_ins | n_tup_upd | n_tup_del | n_live_tup | n_dead_tup
---------+-----------+-----------+-----------+------------+-----------
 t       |      1000 |       500 |         0 |       1000 |        500
(1 row)
```

### Шаг 3: Результат
```
 relname | last_vacuum | last_autovacuum | last_analyze | last_autoanalyze
---------+-------------+-----------------+--------------+-----------------
 t       |             | 2025-06-23...   |              | 2025-06-23...
(1 row)
```

## Контрольные вопросы

1. Что такое `n_dead_tup` и как он влияет на производительность?
2. Как определить, что таблице нужен vacuum?
3. Чем `pg_stat_user_tables` отличается от `pg_stat_all_tables`?
4. Как найти запрос, который блокирует другие транзакции?

## Дополнительное задание

Создайте скрипт мониторинга, который выводит все таблицы с долей мёртвых версий больше 10% и временем последнего автоочистки больше 1 часа назад.