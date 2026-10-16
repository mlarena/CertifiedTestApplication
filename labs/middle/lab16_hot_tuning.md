# Лабораторная работа №16: HOT-обновления и fillfactor

## Цель
Изучить механизм HOT-обновлений, параметр fillfactor, использование pageinspect для анализа страниц и мониторинг HOT через pg_stat_user_tables.

## Теория
HOT (Heap-Only Tuple) — механизм, позволяющий обновлять строку без изменения индекса, если обновляются только неиндексные столбцы. Это экономит место в индексе и ускоряет обновления.

HOT работает только если:
1. Обновляются только неиндексные столбцы
2. Новая версия помещается на той же странице

Параметр `fillfactor` определяет процент страницы, который используется для записи данных. Значение по умолчанию — 100, для таблиц с частыми обновлениями рекомендуется 70-90.

## Задание

### Шаг 1. Создание таблицы с HOT

```sql
CREATE DATABASE lab_hot;
\c lab_hot

CREATE TABLE t(
    id integer PRIMARY KEY,
    val text NOT NULL
);

INSERT INTO t SELECT generate_series(1, 1000), 'value';
```

### Шаг 2. Наблюдение HOT vs non-HOT обновлений

```sql
-- Обновляем неиндексный столбец (HOT возможен)
UPDATE t SET val = 'updated' WHERE id = 1;

-- Обновляем индексированный столбец (HOT невозможен)
UPDATE t SET id = 1001 WHERE id = 1001;

-- Статистика
SELECT n_tup_upd, n_tup_hot_upd
FROM pg_stat_user_tables
WHERE relname = 't';
```

### Шаг 3. Настройка fillfactor

```sql
-- Создание таблицы с fillfactor = 80
CREATE TABLE t2(
    id integer PRIMARY KEY,
    val text NOT NULL
) WITH (fillfactor = 80);

INSERT INTO t2 SELECT generate_series(1, 1000), 'value';

-- Обновляем неиндексные столбцы
UPDATE t2 SET val = 'updated' WHERE id <= 500;

-- HOT-обновления
SELECT n_tup_upd, n_tup_hot_upd
FROM pg_stat_user_tables
WHERE relname = 't2';
```

### Шаг 4. Анализ страниц через pageinspect

```sql
CREATE EXTENSION pageinspect;

-- Количество страниц в таблице
SELECT relpages, reltuples FROM pg_class WHERE relname = 't2';

-- Первая страница
SELECT lp, lp_off, lp_flags, lp_len, t_xmin, t_xmax, t_infomask
FROM heap_page_items(get_page('t2', 0))
LIMIT 10;

-- Поиск HOT-цепочек: lp_off указывает на следующую версию на той же странице
SELECT lp, lp_off, t_xmin, t_xmax, t_infomask & 2048 > 0 AS is_multi
FROM heap_page_items(get_page('t2', 0));
```

### Шаг 5. Влияние fillfactor на размер

```sql
-- Таблица с fillfactor 100 (по умолчанию)
CREATE TABLE t100(
    id integer PRIMARY KEY,
    val text NOT NULL
) WITH (fillfactor = 100);

-- Таблица с fillfactor 70
CREATE TABLE t70(
    id integer PRIMARY KEY,
    val text NOT NULL
) WITH (fillfactor = 70);

INSERT INTO t100 SELECT generate_series(1, 10000), 'value';
INSERT INTO t70 SELECT generate_series(1, 10000), 'value';

-- Сравнение размеров
SELECT
    relname,
    pg_size_pretty(pg_relation_size(oid)) AS size,
    relpages,
    reltuples
FROM pg_class
WHERE relname IN ('t100', 't70');

-- Обновляем все строки в t100 (HOT невозможен)
UPDATE t100 SET val = 'updated';

-- Обновляем все строки в t70 (HOT возможен)
UPDATE t70 SET val = 'updated';

-- Снова размер
SELECT
    relname,
    pg_size_pretty(pg_relation_size(oid)) AS size,
    n_tup_upd, n_tup_hot_upd
FROM pg_class c
JOIN pg_stat_user_tables s ON s.relname = c.relname
WHERE c.relname IN ('t100', 't70');
```

### Шаг 6. Мониторинг HOT-эффективности

```sql
-- Доля HOT-обновлений
SELECT
    relname,
    n_tup_upd,
    n_tup_hot_upd,
    round(n_tup_hot_upd::numeric / nullif(n_tup_upd, 0) * 100, 1) AS hot_pct
FROM pg_stat_user_tables
WHERE n_tup_upd > 0;
```

## Решение

### Шаг 3: Результат
```
 n_tup_upd | n_tup_hot_upd
-----------+---------------
       500 |           500
(1 row)
```

### Шаг 5: Результат
```
 relname | size  | relpages | reltuples
---------+-------+----------+-----------
 t100    | 568 kB|     200  |    10000
 t70     | 456 kB|     160  |    10000
```

## Контрольные вопросы

1. Почему HOT не работает при обновлении индексированных столбцов?
2. Как fillfactor влияет на количество HOT-обновлений?
3. Как `heap_page_items` помогает найти HOT-цепочки?
4. Когда стоит использовать fillfactor < 100?

## Дополнительное задание

Сравните производительность UPDATE на таблице с fillfactor 100 и 70 для 10 000 строк. Измерьте время и количество HOT-обновлений.