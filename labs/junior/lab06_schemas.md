# Лабораторная работа №6: Схемы

## Цель
Изучить систему схем PostgreSQL: создание, путь поиска, перемещение объектов, временные таблицы и специальные схемы.

## Теория
Схема — пространство имен для объектов внутри базы данных. Каждый объект принадлежит какой-либо схеме. Схемы позволяют разделять объекты на логические группы и предотвращать конфликты имен.

Путь поиска (`search_path`) определяет порядок перебора схем при обращении к объектам без явного указания схемы.

## Задание

### Шаг 1. Просмотр текущего пути поиска

```sql
SHOW search_path;
SELECT current_schemas(true);
SELECT current_schema();
```

### Шаг 2. Создание схем

```sql
CREATE DATABASE lab_schemas;
\c lab_schemas

CREATE SCHEMA app;
CREATE SCHEMA "user";
\dn
```

### Шаг 3. Создание таблиц в разных схемах

```sql
CREATE TABLE t(s text);
INSERT INTO t VALUES ('public table');

CREATE TABLE app.t(s text);
INSERT INTO app.t VALUES ('app table');

CREATE TABLE "user".t(s text);
INSERT INTO "user".t VALUES ('user table');
```

### Шаг 4. Обращение к объектам

```sql
-- Текущая таблица (public — первый приоритет по умолчанию)
SELECT * FROM t;

-- Явное указание схемы
SELECT * FROM app.t;
SELECT * FROM "user".t;
```

### Шаг 5. Изменение пути поиска

```sql
SET search_path = public, app, "user";
SELECT * FROM t;  -- public.t

SET search_path = app, public;
SELECT * FROM t;  -- app.t

SET search_path = "$user", public;
```

### Шаг 6. Перемещение объекта между схемами

```sql
ALTER TABLE t SET SCHEMA app;
SELECT * FROM app.t;
-- SELECT * FROM t;  -- ошибка!
```

### Шаг 7. Установка пути поиска на уровне БД

```sql
ALTER DATABASE lab_schemas SET search_path = public, app;
\c lab_schemas
SHOW search_path;
```

### Шаг 8. Временные таблицы

```sql
CREATE TEMP TABLE temp_test(n integer);
INSERT INTO temp_test VALUES (42);

-- Просмотр схемы
SELECT pg_my_temp_schema()::regnamespace;

-- Доступ через pg_temp
SELECT * FROM pg_temp.temp_test;
```

### Шаг 9. Удаление схемы

```sql
DROP SCHEMA "user" CASCADE;
DROP TABLE app.t;
DROP SCHEMA app;
```

## Решение

### Шаг 4: Результат
```
   s
-------------
 public table
(1 row)

     s
--------------
 app table
(1 row)

     s
---------------
 user table
(1 row)
```

## Контрольные вопросы

1. Что такое `$user` в пути поиска и когда он разрешается?
2. Почему временные таблицы не видны другим сеансам?
3. Можно ли удалить схему, содержащую объекты, без `CASCADE`?

## Дополнительное задание

Создайте три схемы (`billing`, `analytics`, `archive`) и переместите в них разные таблицы. Настройте `search_path` на уровне БД так, чтобы `billing` имел приоритет.
