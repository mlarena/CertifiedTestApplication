# Лабораторная работа №9: TOAST

## Цель
Изучить механизм TOAST: стратегии хранения, сжатие,.toast-таблицы, влияние на производительность.

## Теория
TOAST (The Oversized Attributes Storage Technique) — механизм хранения длинных значений, не помещающихся на одну страницу (8 КБ). Стратегии: `plain` (без TOAST), `extended` (сжатие + вынос), `external` (только вынос), `main` (сжатие в последнюю очередь).

## Задание

### Шаг 1. Создание таблицы с текстовым столбцом

```sql
CREATE DATABASE lab_toast;
\c lab_toast

CREATE TABLE toast_test(
    id integer PRIMARY KEY,
    data text
);

\d+ toast_test
```

### Шаг 2. Вставка коротких и длинных строк

```sql
INSERT INTO toast_test VALUES (1, 'Короткая строка');
INSERT INTO toast_test VALUES (2, repeat('A', 5000));
INSERT INTO toast_test VALUES (3, repeat('B', 10000));

SELECT id, length(data) AS len FROM toast_test;
```

### Шаг 3. Проверка toast-таблицы

```sql
-- Путь к toast-таблице
SELECT relname FROM pg_class WHERE oid = (
    SELECT reltoastrelid FROM pg_class WHERE relname = 'toast_test'
);

-- Файлы toast-таблицы
SELECT pg_relation_filepath(reltoastrelid) AS toast_path
FROM pg_class WHERE relname = 'toast_test';
```

### Шаг 4. Содержимое toast-таблицы

```sql
-- Найти OID toast-таблицы
SELECT reltoastrelid::regclass FROM pg_class WHERE relname = 'toast_test';

-- Фрагменты длинных значений
SELECT chunk_id, chunk_seq, length(chunk_data)
FROM pg_toast.pg_toast_<OID_таблицы>
ORDER BY chunk_id, chunk_seq;
```

### Шаг 5. Изменение стратегии

```sql
ALTER TABLE toast_test ALTER COLUMN data SET STORAGE external;

\d+ toast_test

-- Новая вставка
INSERT INTO toast_test VALUES (4, repeat('C', 8000));

-- Размер таблицы не увеличился (данные в toast)
SELECT pg_relation_size('toast_test') AS main_size;
```

### Шаг 6. Сжатие

```sql
-- По умолчанию pglz
SHOW default_toast_compression;

-- Проверка поддержки lz4
SELECT setting, enumvals FROM pg_settings WHERE name = 'default_toast_compression';

-- Установка lz4
ALTER TABLE toast_test ALTER COLUMN data SET COMPRESSION lz4;
```

### Шаг 7. Сравнение размеров

```sql
SELECT
    pg_size_pretty(pg_relation_size('toast_test')) AS main_size,
    pg_size_pretty(pg_indexes_size('toast_test')) AS index_size,
    pg_size_pretty(pg_table_size('toast_test')) AS table_size;
```

## Решение

### Шаг 2: Результат
```
 id |  len
----+------
  1 |    17
  2 |  5000
  3 | 10000
(3 rows)
```

### Шаг 4: Результат
```
 chunk_id | chunk_seq | length
----------+-----------+--------
    16396 |         0 |   1996
    16396 |         1 |   1460
(2 rows)
```

## Контрольные вопросы

1. При каком размере значения попадают в toast-таблицу?
2. В чем разница между стратегиями `extended` и `external`?
3. Как сжатие pglz и lz4 влияют на скорость чтения/записи?

## Дополнительное задание

Сравните время вставки и размер таблицы для трёх стратегий хранения (extended, external, main) с текстовыми данными ~1 МБ.
