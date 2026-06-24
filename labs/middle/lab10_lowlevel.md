# Лабораторная работа №10: Файлы данных

## Цель
Изучить низкоуровневую организацию данных: слои (forks), сегменты, файловая структура, pg_relation_size, pg_relation_filepath.

## Теория
Каждый объект БД на диске представлен несколькими слоями: `main` (данные), `vm` (карта видимости), `fsm` (карта свободного пространства). Файлы делятся на сегменты по 1 ГБ. Файловая структура зависит от табличного пространства.

## Задание

### Шаг 1. Создание таблицы

```sql
CREATE DATABASE lab_lowlevel;
\c lab_lowlevel

CREATE TABLE t(
    id integer PRIMARY KEY,
    data text
);

INSERT INTO t SELECT id, md5(id::text) FROM generate_series(1, 10000);
VACUUM t;
```

### Шаг 2. Путь к файлам

```sql
-- Относительный путь от PGDATA
SELECT pg_relation_filepath('t');
```

### Шаг 3. Файлы в файловой системе

```sql
-- Просмотр файлов (от имени postgres)
\! sudo -u postgres ls -l /var/lib/postgresql/16/main/base/$(oid)/$(filenode)*

-- Или через SQL
SELECT relfilenode, relname FROM pg_class WHERE relname = 't';
\! sudo -u postgres ls -l /var/lib/postgresql/16/main/base/16386/16388*
```

### Шаг 4. Размеры отдельных слоёв

```sql
SELECT
    pg_relation_size('t', 'main') AS main,
    pg_relation_size('t', 'fsm') AS fsm,
    pg_relation_size('t', 'vm') AS vm;
```

### Шаг 5. Индексы и последовательности

```sql
-- Файлы индекса
SELECT pg_relation_filepath('t_pkey');

-- Файлы последовательности
SELECT pg_relation_filepath(pg_get_serial_sequence('t', 'id'));
```

### Шаг 6. Размеры с учётом toast и индексов

```sql
SELECT
    pg_size_pretty(pg_table_size('t')) AS table_size,
    pg_size_pretty(pg_indexes_size('t')) AS indexes_size,
    pg_size_pretty(pg_total_relation_size('t')) AS total_size;
```

### Шаг 7. Временные таблицы

```sql
CREATE TEMP TABLE temp_t AS SELECT * FROM t;
VACUUM temp_t;

SELECT pg_relation_filepath('temp_t');
\! sudo -u postgres ls -l /var/lib/postgresql/16/main/base/16386/t4_16397*
```

### Шаг 8. oid2name

```bash
# Все базы данных
/usr/lib/postgresql/16/bin/oid2name

# Объекты в базе
/usr/lib/postgresql/16/bin/oid2name -d lab_lowlevel

# По имени таблицы
/usr/lib/postgresql/16/bin/oid2name -d lab_lowlevel -t t
```

## Решение

### Шаг 2: Результат
```
pg_relation_filepath
----------------------
base/16386/16388
(1 row)
```

### Шаг 4: Результат
```
  main   |   fsm   |    vm
---------+---------+---------
  450560 |   24576 |    8192
(1 row)
```

## Контрольные вопросы

1. Зачем файлы данных делятся на сегменты по 1 ГБ?
2. В каких случаях создаётся слой `_init`?
3. Чем временные таблицы отличаются от постоянных на уровне файлов?

## Дополнительное задание

Создайте нежурналируемую таблицу (`UNLOGGED`) и убедитесь, что для неё существует слой `_init`.
