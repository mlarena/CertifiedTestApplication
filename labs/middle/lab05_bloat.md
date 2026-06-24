# Лабораторная работа №5: Разрастание таблиц и индексов

## Цель
Научиться оценивать разрастание (bloat) таблиц и индексов с помощью pgstattuple, pgstatindex и системного каталога.

## Теория
Разрастание возникает из-за накопления мертвых версий строк и разделения страниц индексов. VACUUM удаляет мертвые строки, но не возвращает место ОС. Для уменьшения размера требуются VACUUM FULL или REINDEX.

## Задание

### Шаг 1. Создание таблицы с разрастанием

```sql
CREATE DATABASE lab_bloat;
\c lab_bloat

CREATE EXTENSION pgstattuple;

CREATE TABLE bloat_test(
    id integer PRIMARY KEY,
    data text
);

INSERT INTO bloat_test
SELECT id, md5(id::text) FROM generate_series(1, 100000) AS id;

CREATE INDEX idx_bloat ON bloat_test(data);
```

### Шаг 2. Оценка начального состояния

```sql
SELECT tuple_count, dead_tuple_count, free_percent, dead_tuple_percent
FROM pgstattuple('bloat_test');

SELECT tree_level, leaf_pages, avg_leaf_density, leaf_fragmentation
FROM pgstatindex('idx_bloat');
```

### Шаг 3. Создание разрастания

```sql
-- Обновляем все строки
UPDATE bloat_test SET data = md5(data);
UPDATE bloat_test SET data = md5(data);
UPDATE bloat_test SET data = md5(data);

-- Проверяем
SELECT dead_tuple_count, dead_tuple_percent
FROM pgstattuple('bloat_test');

SELECT leaf_pages, avg_leaf_density
FROM pgstatindex('idx_bloat');
```

### Шаг 4. Оценка через pgstattuple_approx

```sql
SELECT approx_tuple_count, approx_free_percent, approx_dead_tuple_percent
FROM pgstattuple_approx('bloat_test');
```

### Шаг 5. Оценка через системный каталог

```sql
-- Приблизительный размер таблицы
SELECT relpages, reltuples,
       pg_size_pretty(pg_relation_size('bloat_test')) AS size
FROM pg_class WHERE relname = 'bloat_test';
```

### Шаг 6. Восстановление

```sql
-- Обычная очистка
VACUUM bloat_test;
SELECT dead_tuple_count FROM pgstattuple('bloat_test');

-- Перестроение индекса
REINDEX TABLE CONCURRENTLY bloat_test;
SELECT leaf_pages, avg_leaf_density FROM pgstatindex('idx_bloat');

-- Полная очистка таблицы
VACUUM FULL bloat_test;
SELECT free_percent FROM pgstattuple('bloat_test');
```

## Решение

### Шаг 3: Результат
```
 tuple_count | dead_tuple_count | free_percent | dead_tuple_percent
-------------+------------------+--------------+-------------------
      100000 |           100000 |         0.32 |              30.10
```

## Контрольные вопросы

1. Почему `pgstattuple` может показывать неточные данные для больших таблиц?
2. В каких случаях `REINDEX CONCURRENTLY` предпочтительнее `REINDEX`?
3. Что такое `leaf_fragmentation` и когда это проблема?

## Дополнительное задание

Напишите SQL-запрос, который для всех пользовательских таблиц показывает: размер, количество живых/мертвых строк, процент свободного места.
