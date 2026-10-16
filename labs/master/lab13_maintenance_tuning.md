# Лабораторная работа №13: Настройка обслуживания и автоочистки

## Цель
Настроить параметры обслуживания: maintenance_work_mem, autovacuum_work_mem, vacuum_cost_delay, cost_limit, мониторинг через pg_stat_progress_vacuum.

## Теория
Параметры обслуживания влияют на производительность VACUUM, ANALYZE, CREATE INDEX, ALTER TABLE.

- `maintenance_work_mem` — память для VACUUM, CREATE INDEX, ALTER TABLE (по умолчанию 64MB)
- `autovacuum_work_mem` — память для автоочистки (по умолчанию -1 → maintenance_work_mem)
- `autovacuum_vacuum_cost_delay` — задержка при автоочистке (по умолчанию 2ms)
- `autovacuum_vacuum_cost_limit` — лимит стоимости (по умолчанию 200)

## Задание

### Шаг 1. Текущие параметры обслуживания

```sql
-- Параметры обслуживания
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name IN (
    'maintenance_work_mem',
    'autovacuum_work_mem',
    'autovacuum_vacuum_cost_delay',
    'autovacuum_vacuum_cost_limit',
    'autovacuum_max_workers'
)
ORDER BY name;
```

### Шаг 2. Настройка maintenance_work_mem

```sql
-- Настройка для сеанса
SET maintenance_work_mem TO '256MB';

-- Настройка для базы
ALTER DATABASE lab_db SET maintenance_work_mem TO '512MB';

-- Настройка глобально
ALTER SYSTEM SET maintenance_work_mem TO '1GB';
SELECT pg_reload_conf();
```

### Шаг 3. Настройка автоочистки

```sql
-- Параметры автоочистки
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE 'autovacuum%'
ORDER BY name;

-- Настройка задержки
ALTER SYSTEM SET autovacuum_vacuum_cost_delay TO '10ms';
ALTER SYSTEM SET autovacuum_vacuum_cost_limit TO '1000';
SELECT pg_reload_conf();
```

### Шаг 4. Создание таблицы с большой статистикой

```sql
CREATE DATABASE lab_maintenance;
\c lab_maintenance

CREATE TABLE big_table(
    id integer PRIMARY KEY,
    val text,
    created_at timestamptz DEFAULT now()
);

-- Вставка 1M строк
INSERT INTO big_table SELECT generate_series(1, 1000000), md5(random()::text);

-- Обновление 50% строк
UPDATE big_table SET val = 'updated' WHERE id % 2 = 0;

-- Проверка статистики
SELECT relname, n_live_tup, n_dead_tup, n_tup_upd, last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'big_table';
```

### Шаг 5. Мониторинг VACUUM через pg_stat_progress_vacuum

```sql
-- Запуск vacuum с мониторингом
VACUUM (VERBOSE, ANALYZE) big_table;

-- В другом сеансе:
SELECT phase, heap_blks_total, heap_blks_scanned,
       heap_blks_vacuumed, index_vacuum_count,
       num_deadlocks
FROM pg_stat_progress_vacuum;
```

### Шаг 6. Настройка per-table параметров

```sql
-- Настройка для конкретной таблицы
ALTER TABLE big_table SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_threshold = 10000,
    autovacuum_analyze_scale_factor = 0.05,
    autovacuum_freeze_min_age = 1000000,
    fillfactor = 80
);

-- Проверка
SELECT reloptions FROM pg_class WHERE relname = 'big_table';
```

### Шаг 7. Настройка ANALYZE

```sql
-- Параметры ANALYZE
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE 'default_statistics_target'
   OR name LIKE 'autovacuum_analyze%'
ORDER BY name;

-- Настройка
ALTER TABLE big_table SET (default_statistics_target = 500);
-- (повышает точность статистики, но замедляет ANALYZE)

-- Проверка
SELECT relname, attname, attstattarget
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
WHERE relname = 'big_table' AND attstattarget > 0;
```

### Шаг 8. Мониторинг автоочистки

```sql
-- Статистика автоочистки
SELECT relname,
       n_tup_ins, n_tup_upd, n_tup_del,
       n_dead_tup,
       n_mod_since_analyze,
       last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_autovacuum IS NULL;
```

## Решение

### Шаг 5: Результат
```
 phase    | heap_blks_total | heap_blks_scanned | heap_blks_vacuumed
----------+-----------------+-------------------+-------------------
 vacuum   | 1000            | 800               | 600
```

## Контрольные вопросы

1. Чем maintenance_work_mem отличается от autovacuum_work_mem?
2. Как cost_delay влияет на производительность?
3. Что делает pg_stat_progress_vacuum?
4. Как настроить автоочистку для конкретной таблицы?

## Дополнительное задание

Создайте скрипт мониторинга, который выводит все таблицы, не прошедшие автоочистку более 24 часов назад.