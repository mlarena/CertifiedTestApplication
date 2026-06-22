# Лабораторная работа №12: pg_stat_statements

## Цель
Установить и использовать расширение pg_stat_statements для анализа производительности запросов.

## Теория
`pg_stat_statements` — расширение,追踪执行的所有 SQL-запросов и собирающее статистику: количество вызовов, общее время, время планирования и выполнения, количество возвратенных строк.

Для работы требует загрузки модуля через `shared_preload_libraries` и перезапуска сервера.

## Задание

### Шаг 1. Установка модуля

```sql
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
```

```bash
sudo pg_ctlcluster 16 main restart
```

### Шаг 2. Создание расширения

```sql
CREATE DATABASE lab_statements;
\c lab_statements

CREATE EXTENSION pg_stat_statements;
```

### Шаг 3. Нагрузка

```sql
CREATE TABLE t(n integer);
INSERT INTO t SELECT id FROM generate_series(1, 10000);

-- Выполняем разные запросы
SELECT count(*) FROM t WHERE n > 5000;
SELECT count(*) FROM t WHERE n > 5000;
SELECT count(*) FROM t WHERE n > 5000;
SELECT * FROM t ORDER BY n DESC LIMIT 10;
DELETE FROM t WHERE n < 1000;
DELETE FROM t WHERE n < 1000;
```

### Шаг 4. Анализ статистики

```sql
-- Самые частые запросы
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 5;

-- Самые медленные запросы
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 5;
```

### Шаг 5. Детальный анализ

```sql
SELECT query, calls, rows,
       shared_blks_hit, shared_blks_read,
       temp_blks_written
FROM pg_stat_statements
WHERE query LIKE '%t%'
ORDER BY calls DESC;
```

### Шаг 6. Сброс статистики

```sql
SELECT pg_stat_statements_reset();

-- Проверяем
SELECT count(*) FROM pg_stat_statements;
```

## Решение

### Шаг 4: Результат
```
                query                 | calls | total_exec_time | mean_exec_time | rows
--------------------------------------+-------+-----------------+----------------+-----
 SELECT count(*) FROM t WHERE n > $1 |     3 |         0.17070 |      0.05690  |    3
 DELETE FROM t WHERE n < $1          |     2 |         0.12345 |      0.06172  |    2
(2 rows)
```

## Контрольные вопросы

1. Зачем нужен `shared_preload_libraries` для pg_stat_statements?
2. Что такое `mean_exec_time` и когда оно полезно?
3. Как pg_stat_statements влияет на производительность?

## Дополнительное задание

Настройте `pg_stat_statements.max = 10000` и `pg_stat_statements.track = all`. Сравните статистику с включённым и выключенным `track`.
