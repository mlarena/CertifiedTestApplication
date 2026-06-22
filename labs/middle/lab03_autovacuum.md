# Лабораторная работа №3: Автоочистка (Autovacuum)

## Цель
Изучить механизм автоочистки: назначение, настройка параметров, мониторинг, влияние на производительность.

## Теория
Autovacuum — фоновый процесс, который автоматически очищает мертвые версии строк, обновляет карты видимости и свободного пространства, а также собирает статистику. Отключение autovacuum приводит к разрастанию таблиц и деградации производительности.

## Задание

### Шаг 1. Мониторинг autovacuum

```sql
CREATE DATABASE lab_autovacuum;
\c lab_autovacuum

-- Проверяем, что autovacuum работает
SELECT pid, backend_type, backend_start
FROM pg_stat_activity
WHERE backend_type LIKE 'autovacuum%';
```

### Шаг 2. Отключение autovacuum для таблицы

```sql
CREATE TABLE bloat_test(
    id integer GENERATED ALWAYS AS IDENTITY,
    data text
) WITH (autovacuum_enabled = off);

INSERT INTO bloat_test(data)
SELECT md5(random()::text) FROM generate_series(1, 100000);
```

### Шаг 3. Наблюдение за разрастанием

```sql
SELECT pg_size_pretty(pg_table_size('bloat_test')) AS size;

-- Обновляем половину строк
UPDATE bloat_test SET data = md5(random()::text) WHERE id <= 50000;

SELECT pg_size_pretty(pg_table_size('bloat_test')) AS size;

-- Еще раз
UPDATE bloat_test SET data = md5(random()::text) WHERE id <= 50000;
SELECT pg_size_pretty(pg_table_size('bloat_test')) AS size;
```

### Шаг 4. Ручная очистка

```sql
VACUUM VERBOSE bloat_test;

SELECT pg_size_pretty(pg_table_size('bloat_test')) AS size;
```

### Шаг 5. Статистика автоочистки

```sql
SELECT relname, n_live_tup, n_dead_tup,
       last_autovacuum, last_autoanalyze,
       autovacuum_count, autoanalyze_count
FROM pg_stat_user_tables
WHERE relname = 'bloat_test';
```

### Шаг 6. Настройка параметров

```sql
-- Просмотр текущих настроек
SHOW autovacuum;
SHOW autovacuum_vacuum_threshold;
SHOW autovacuum_vacuum_scale_factor;
SHOW autovacuum_analyze_threshold;
SHOW autovacuum_analyze_scale_factor;

-- Изменение для конкретной таблицы
ALTER TABLE bloat_test SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_analyze_scale_factor = 0.01
);
```

### Шаг 7. pgstattuple

```sql
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT tuple_count, dead_tuple_count, free_percent
FROM pgstattuple('bloat_test');
```

## Решение

### Шаг 3: Результат
```
-- После первой вставки:
 size
--------
 4360 kB

-- После первого UPDATE:
 size
--------
 6512 kB

-- После второго UPDATE:
 size
--------
 8664 kB
```

### Шаг 5: Результат
```
   relname    | n_live_tup | n_dead_tup | last_autovacuum
--------------+------------+------------+-----------------
 bloat_test   |     100000 |     100000 | ...
(1 row)
```

## Контрольные вопросы

1. Почему autovacuum не уменьшает физический размер файла таблицы?
2. Что такое `autovacuum_vacuum_scale_factor` и как он влияет на частоту очистки?
3. Почему отключение autovacuum — плохая идея?

## Дополнительное задание

Настройте autovacuum так, чтобы очистка запускалась чаще при активных обновлениях таблицы. Сравните размер до и после настройки.
