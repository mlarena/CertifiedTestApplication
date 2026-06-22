# Лабораторная работа №4: VACUUM и ANALYZE

## Цель
Научиться выполнять ручную очистку (VACUUM), анализ (ANALYZE) и полную очистку (VACUUM FULL), понимать их различия и последствия.

## Теория
- `VACUUM` — очистка мертвых версий строк без блокировки таблицы
- `ANALYZE` — сбор статистики для планировщика запросов
- `VACUUM FULL` — полное перестроение таблицы с блокировкой
- `REINDEX` — перестроение индексов

## Задание

### Шаг 1. Создание тестовой таблицы

```sql
CREATE DATABASE lab_vacuum;
\c lab_vacuum

CREATE TABLE test_vac(n integer, s text);
INSERT INTO test_vac SELECT id, md5(id::text) FROM generate_series(1, 100000) AS id;
CREATE INDEX idx_test_vac ON test_vac(n);
```

### Шаг 2. Наблюдение за мёртвыми строками

```sql
UPDATE test_vac SET s = md5(s) WHERE id <= 50000;

-- Статистика
SELECT n_live_tup, n_dead_tup
FROM pg_stat_user_tables WHERE relname = 'test_vac';
```

### Шаг 3. Обычная очистка

```sql
VACUUM test_vac;

-- Статистика после очистки
SELECT n_live_tup, n_dead_tup
FROM pg_stat_user_tables WHERE relname = 'test_vac';

-- Размер файла
SELECT pg_size_pretty(pg_table_size('test_vac')) AS size;
```

### Шаг 4. Полная очистка

```sql
VACUUM FULL test_vac;

-- Размер файла после VACUUM FULL
SELECT pg_size_pretty(pg_table_size('test_vac')) AS size;
```

### Шаг 5. Анализ

```sql
-- Удаляем статистику
ALTER TABLE test_vac ALTER COLUMN n SET STATISTICS 0;
ANALYZE test_vac;

-- Проверка
SELECT attname, n_distinct, most_common_vals
FROM pg_stats WHERE tablename = 'test_vac' AND attname = 'n';
```

### Шаг 6. REINDEX

```sql
-- Индекс разрастается при обновлениях
UPDATE test_vac SET n = n + 1 WHERE id % 2 = 0;
SELECT pg_size_pretty(pg_indexes_size('test_vac')) AS index_size;

-- Перестроение
REINDEX TABLE CONCURRENTLY test_vac;
SELECT pg_size_pretty(pg_indexes_size('test_vac')) AS index_size;
```

### Шаг 7. VACUUM VERBOSE

```sql
VACUUM (VERBOSE, ANALYZE) test_vac;
```

## Решение

### Шаг 3: Результат
```
-- До VACUUM:
 n_live_tup | n_dead_tup
------------+------------
     100000 |      50000

-- После VACUUM:
 n_live_tup | n_dead_tup
------------+------------
     100000 |          0

-- Размер:
 size
--------
 8664 kB
```

### Шаг 4: Результат
```
-- После VACUUM FULL:
 size
--------
 4336 kB
```

## Контрольные вопросы

1. Почему VACUUM FULL уменьшает размер, а обычный VACUUM — нет?
2. Чем `REINDEX CONCURRENTLY` отличается от обычного `REINDEX`?
3. Когда использовать VACUUM ANALYZE вместо раздельных команд?

## Дополнительное задание

Сравните время выполнения VACUUM и VACUUM FULL на таблице с 1 млн строк. Используйте `\timing on`.
