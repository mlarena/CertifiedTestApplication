# Лабораторная работа №12: Системный каталог

## Цель
Научиться работать с системным каталогом PostgreSQL: основные таблицы, типы oid, команды psql для описания объектов.

## Теория
Системный каталог — набор таблиц и представлений, описывающих все объекты кластера. Расположен в схеме `pg_catalog`. Альтернативное представление — `information_schema` (стандарт SQL).

Основные таблицы: `pg_class` (отношения), `pg_attribute` (столбцы), `pg_namespace` (схемы), `pg_database` (базы данных), `pg_tablespace` (табличные пространства).

## Задание

### Шаг 1. Создание тестовых объектов

```sql
CREATE DATABASE lab_catalog;
\c lab_catalog

CREATE TABLE employees(
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    department text
);

CREATE VIEW active_employees AS
SELECT * FROM employees WHERE department IS NOT NULL;

CREATE INDEX idx_emp_dept ON employees(department);
```

### Шаг 2. Просмотр через psql

```sql
-- Таблицы
\dt

-- Индексы
\di

-- Представления
\dv

-- Все объекты
\dtvis

-- Подробное описание таблицы
\d+ employees
```

### Шаг 3. Запросы к системному каталогу

```sql
-- Информация о таблице из pg_class
SELECT relname, relkind, relnamespace, relowner
FROM pg_class WHERE relname = 'employees';

-- relkind: r=таблица, i=индекс, v=представление, S=последовательность
SELECT relname,
    CASE relkind
        WHEN 'r' THEN 'таблица'
        WHEN 'v' THEN 'представление'
        WHEN 'i' THEN 'индекс'
        WHEN 'S' THEN 'последовательность'
    END AS тип
FROM pg_class
WHERE relnamespace = 'public'::regnamespace
ORDER BY relkind;
```

### Шаг 4. Столбцы таблицы

```sql
SELECT a.attname, pg_catalog.format_type(a.atttypid, a.atttypmod) AS type
FROM pg_attribute a
WHERE a.attrelid = 'employees'::regclass
AND a.attnum > 0
ORDER BY a.attnum;
```

### Шаг 5. Reg-типы

```sql
-- Преобразование имени в oid
SELECT 'employees'::regclass::oid;

-- oid обратно в имя
SELECT 16388::regclass;

-- Тип столбца
SELECT attname, atttypid::regtype
FROM pg_attribute
WHERE attrelid = 'employees'::regclass AND attnum > 0;
```

### Шаг 6. Скрытые SQL-запросы psql

```sql
\set ECHO_HIDDEN on
\dt employees
\set ECHO_HIDDEN off
```

## Решение

### Шаг 3: Результат
```
 relname    | relkind | relnamespace | relowner
------------+---------+--------------+----------
 employees  | r       |         2200 |    16384
 active_employees | v  |         2200 |    16384
 idx_emp_dept | i     |         2200 |    16384
 employees_id_seq | S |         2200 |    16384
(4 rows)
```

## Контрольные вопросы

1. Какие значения принимает `relkind` и что они означают?
2. Зачем нужен тип `regclass` и как он работает?
3. Что такое `pg_attribute` и как получить столбцы таблицы через него?

## Дополнительное задание

Напишите SQL-запрос, который для каждой пользовательской таблицы показывает количество столбцов, размер и последний анализ.
