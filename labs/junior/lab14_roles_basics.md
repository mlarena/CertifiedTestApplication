# Лабораторная работа №14: Роли

## Цель
Научиться создавать роли, управлять атрибутами (LOGIN, SUPERUSER, CREATEDB), использовать встроенные команды psql для просмотра ролей.

## Теория
В PostgreSQL роль может быть пользователем (атрибут LOGIN) или группой (NOLOGIN). Роли могут быть включены друг в друга, что позволяет управлять наборами привилегий. Атрибуты: LOGIN, SUPERUSER, CREATEDB, CREATEROLE, REPLICATION, BYPASSRLS и др.

## Задание

### Шаг 1. Просмотр ролей

```sql
-- Все роли
\du

-- Все роли, включая системные
\duS
```

### Шаг 2. Создание ролей

```sql
CREATE ROLE lab_admin LOGIN PASSWORD 'admin123' CREATEDB;
CREATE ROLE lab_user LOGIN PASSWORD 'user123';
CREATE ROLE lab_readonly NOLOGIN;

-- Проверка
\du
```

### Шаг 3. Изменение атрибутов

```sql
-- Добавление атрибута
ALTER ROLE lab_user CREATEDB;

-- Смена пароля
ALTER ROLE lab_user PASSWORD 'newpass456';

-- Отключение входа
ALTER ROLE lab_user NOLOGIN;

-- Включение обратно
ALTER ROLE lab_user LOGIN;
```

### Шаг 4. Групповые роли

```sql
-- Включение lab_user в группу lab_readonly
GRANT lab_readonly TO lab_user;

-- Просмотр включений
\drg
```

### Шаг 5. Просмотр свойств роли

```sql
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin, rolreplication
FROM pg_authid
WHERE rolname LIKE 'lab_%';
```

### Шаг 6. Удаление ролей

```sql
REVOKE lab_readonly FROM lab_user;
DROP ROLE lab_readonly;
DROP ROLE lab_user;
DROP ROLE lab_admin;
```

## Решение

### Шаг 5: Результат
```
 rolname  | rolsuper | rolcreaterole | rolcreatedb | rolcanlogin | rolreplication
----------+----------+---------------+-------------+-------------+----------------
 lab_admin| f        | f             | t           | t           | f
 lab_readonly | f     | f             | f           | f           | f
 lab_user | f        | f             | f           | t           | f
(3 rows)
```

## Контрольные вопросы

1. Чем роль с атрибутом LOGIN отличается от роли без него?
2. Можно ли удалить роль, которая является владельцем объектов?
3. Как проверить, в какие группы включена роль?

## Дополнительное задание

Создайте три роли (reader, writer, admin) и настройте иерархию: reader и writer включены в admin. Проверьте наследование привилегий.
