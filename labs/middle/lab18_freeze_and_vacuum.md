# Лабораторная работа №18: Заморозка транзакций и VACUUM

## Цель
Изучить механизм заморозки (freeze) транзакций, параметры ages, мониторинг через pg_stat_progress_vacuum, понимание per-table параметров.

## Теория
PostgreSQL использует 32-битный счётчик транзакций. Когда счётчик приближается к переполнению, старые транзакции необходимо заморозить: заменить `xmin` на специальный `FrozenTransactionId`, чтобы версия строки стала «вечно видимой».

Ключевые параметры:
- `vacuum_freeze_min_age` — минимальный возраст (по умолчанию 50M)
- `vacuum_freeze_table_age` — возраст таблицы для полной заморозки (150M)
- `vacuum_freeze_max_age` — максимальный возраст до принудительной заморозки (200M)

## Задание

### Шаг 1. Возраст транзакций

```sql
CREATE DATABASE lab_freeze;
\c lab_freeze

CREATE TABLE t(id integer PRIMARY KEY, val text);
INSERT INTO t SELECT generate_series(1, 1000), 'value';

-- Текущий номер транзакции
SELECT txid_current();

-- Возраст транзакции
SELECT txid_current() - 1 AS current_xid,
       age(txid_current()::text::bigint) AS current_age;

-- Возраст таблицы (xmin)
SELECT relname, age(relfrozenxid) AS table_age
FROM pg_class
WHERE relname = 't';
```

### Шаг 2. Параметры заморозки

```sql
-- Текущие значения параметров
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE '%freeze%age%'
ORDER BY name;

-- Настройка для таблицы
ALTER TABLE t SET (autovacuum_freeze_min_age = 100000);
ALTER TABLE t SET (autovacuum_freeze_table_age = 200000);
ALTER TABLE t SET (autovacuum_freeze_max_age = 300000);

-- Проверка
SELECT reloptions FROM pg_class WHERE relname = 't';
```

### Шаг 3. VACUUM и мониторинг через pg_stat_progress_vacuum

```sql
-- Таблица с большим количеством строк
CREATE TABLE big_table(id integer PRIMARY KEY, val text);
INSERT INTO big_table SELECT generate_series(1, 1000000), md5(random()::text);

-- Обновляем 50% строк для создания мёртвых версий
UPDATE big_table SET val = 'updated' WHERE id % 2 = 0;

-- Запускаем vacuum в одном сеансе
VACUUM (verbose, analyze) big_table;

-- В другом сеансе (пока vacuum работает):
SELECT phase, heap_blks_total, heap_blks_scanned, heap_blks_vacuumed,
       index_vacuum_count, max_deadlocks, num_deadlocks
FROM pg_stat_progress_vacuum;
```

### Шаг 4. VACUUM FULL и заморозка

```sql
-- Текущий размер
SELECT pg_size_pretty(pg_relation_size('big_table'));

-- VACUUM FULL (требует ACCESS EXCLUSIVE)
VACUUM FULL big_table;

-- Размер после
SELECT pg_size_pretty(pg_relation_size('big_table'));
```

### Шаг 5. Принудительная заморозка

```sql
-- VACUUM (freeze) — полная заморозка всех версий
VACUUM (freeze, verbose) t;

-- Проверка возраста
SELECT relname, age(relfrozenxid) AS table_age
FROM pg_class
WHERE relname = 't';

-- Проверка через pageinspect
SELECT t_xmin, t_xmax, t_infomask
FROM heap_page_items(get_page('t', 0))
LIMIT 5;
-- t_xmin должен быть 2 (FrozenTransactionId)
```

### Шаг 6. Отслеживание datfrozenxid

```sql
-- Возраст базы данных
SELECT datname, age(datfrozenxid) AS db_age
FROM pg_database
WHERE datname = current_database();

-- Все таблицы с возрастом
SELECT
    schemaname,
    relname,
    age(relfrozenxid) AS age,
    n_live_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 20;
```

### Шаг 7. Failsafe-режим

```sql
-- Failsafe: при достижении age > autovacuum_freeze_max_age
-- автоочистка игнорирует vacuum cost delay

-- Проверка (нужны большие age)
SELECT name, setting
FROM pg_settings
WHERE name IN (
    'autovacuum_freeze_max_age',
    'vacuum_freeze_min_age',
    'vacuum_freeze_table_age',
    'autovacuum_vacuum_cost_delay'
);
```

## Решение

### Шаг 2: Результат
```
 name                     | setting   | unit | short_desc
--------------------------+-----------+------+---------------------------
 vacuum_freeze_min_age    | 50000000  |      | Minimum age...
 vacuum_freeze_table_age  | 150000000 |      | Maximum age...
 autovacuum_freeze_max_age| 200000000 |      | Maximum age...
```

### Шаг 6: Результат
```
 schemaname | relname   | age     | n_live_tup | last_vacuum
------------+-----------+---------+------------+-------------
 public     | t         | 1000000 | 1000       | 2025-06-23...
 public     | big_table | 500000  | 1000000    |
```

## Контрольные вопросы

1. Что произойдёт при переполнении счётчика транзакций?
2. Чем `VACUUM` отличается от `VACUUM FREEZE`?
3. Когда включается failsafe-режим автоочистки?
4. Как `relfrozenxid` отличается от `datfrozenxid`?

## Дополнительное задание

Создайте скрипт, который проверяет возраст всех таблиц и предупреждает, если возраст превышает 150 000 000 транзакций.