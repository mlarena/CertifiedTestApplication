# Лабораторная работа №15: Привилегии — основы

## Цель
Освоить основы управления доступом: GRANT и REVOKE привилегий на таблицы, схемы, базы данных.

## Теория
Привилегии определяют права доступа ролей к объектам. Для таблиц: SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER. Для схем: CREATE, USAGE. Для БД: CREATE, CONNECT, TEMPORARY.

Категории ролей: суперпользователи (полный доступ), владельцы объектов (все привилегии + неотъемлемые права), остальные роли (только выданные привилегии).

## Задание

### Шаг 1. Создание окружения

```sql
CREATE DATABASE lab_privileges;
\c lab_privileges

CREATE ROLE alice LOGIN PASSWORD 'alice123';
CREATE ROLE bob LOGIN PASSWORD 'bob123';

CREATE TABLE products(
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text,
    price numeric
);

INSERT INTO products(name, price) VALUES ('Laptop', 999), ('Phone', 599);
```

### Шаг 2. Проверка привилегий по умолчанию

```sql
-- Боб не может обратиться к таблице
SET ROLE bob;
SELECT * FROM products;  -- ОШИБКА!
RESET ROLE;
```

### Шаг 3. Предоставление привилегий

```sql
-- Alice — полный доступ
GRANT ALL ON products TO alice;

-- Bob — только чтение
GRANT SELECT ON products TO bob;

-- Просмотр привилегий
\dp products
```

### Шаг 4. Проверка

```sql
SET ROLE bob;
SELECT * FROM products;  -- OK
INSERT INTO products(name, price) VALUES ('Tablet', 299);  -- ОШИБКА!
RESET ROLE;

SET ROLE alice;
SELECT * FROM products;  -- OK
INSERT INTO products(name, price) VALUES ('Tablet', 299);  -- OK
RESET ROLE;
```

### Шаг 5. Отзыв привилегий

```sql
REVOKE SELECT ON products FROM bob;
SET ROLE bob;
SELECT * FROM products;  -- ОШИБКА!
RESET ROLE;
```

### Шаг 6. Привилегии на схему

```sql
-- Создадим схему для Alice
CREATE SCHEMA alice_schema;
GRANT ALL ON SCHEMA alice_schema TO alice;

-- Bob получает только USAGE
GRANT USAGE ON SCHEMA alice_schema TO bob;

-- Alice создаёт таблицу в своей схеме
SET ROLE alice;
CREATE TABLE alice_schema.t1(n integer);
RESET ROLE;

-- Bob может читать, но не писать
SET ROLE bob;
SELECT * FROM alice_schema.t1;  -- OK
INSERT INTO alice_schema.t1 VALUES (1);  -- ОШИБКА!
RESET ROLE;
```

### Шаг 7. Удаление

```sql
DROP SCHEMA alice_schema CASCADE;
DROP TABLE products;
DROP ROLE alice;
DROP ROLE bob;
```

## Решение

### Шаг 3: Результат
```
\dp products
                               Access privileges
 Schema |   Name   | Type  | Access privileges  | Column privileges | Policies
--------+----------+-------+--------------------+-------------------+----------
 public | products | table | postgres=arwdDxt/postgres+ |        |
        |          |       | bob=r/postgres     |                   |
        |          |       | alice=arwdDxt/postgres     |        |
(1 row)
```

## Контрольные вопросы

1. Что такое псевдороль `public` и какие привилегии она имеет по умолчанию?
2. Как проверить, есть ли у роли определённая привилегия?
3. Чем GRANT ALL ON SCHEMA отличается от GRANT ALL ON TABLE?

## Дополнительное задание

Настройте привилегии по умолчанию (`ALTER DEFAULT PRIVILEGES`) так, чтобы Bob автоматически получал SELECT на все новые таблицы, создаваемые Alice.
