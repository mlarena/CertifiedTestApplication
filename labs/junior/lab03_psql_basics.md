# Лабораторная работа №3: Основы psql

## Цель
Освоить терминальный клиент psql: подключение, навигация, основные команды для работы с базами данных и системным каталогом.

## Теория
`psql` — основной инструмент для работы с PostgreSQL. Это терминальный клиент, который позволяет выполнять команды SQL и собственные команды psql (начинаются с обратной косой черты `\`). Команды psql можно сокращать до первой буквы.

Параметры подключения по умолчанию: база данных = имя пользователя ОС, пользователь = имя пользователя ОС, порт = 5432.

## Задание

### Шаг 1. Запуск psql и информация о подключении

```bash
psql -U postgres
```

```sql
\conninfo
```

### Шаг 2. Получение справки

```sql
-- Список команд psql
\?

-- Список команд SQL
\h

-- Справка по конкретной команде
\h CREATE DATABASE

-- Выход
\q
```

### Шаг 3. Просмотр баз данных

```sql
-- Краткий список
\l

-- Подробный список (с размерами)
\l+

-- Подключение к конкретной базе
\c postgres
```

### Шаг 4. Просмотр схем и таблиц

```sql
-- Список схем
\dn

-- Список таблиц
\dt

-- Список таблиц со всеми объектами
\dtvis

-- Подробное описание таблицы
\d pg_class

-- С размерами
\d+ pg_class
```

### Шаг 5. Выполнение SQL-запросов

```sql
SELECT version();

SELECT datname, pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- Проверка текущей роли
SELECT current_user, current_database();
```

### Шаг 6. Форматирование вывода

```sql
-- Расширенный формат (для одной записи)
\x
SELECT * FROM pg_database WHERE datname = current_database();
\x off

-- Одноразовый расширенный формат
SELECT * FROM pg_database WHERE datname = current_database() \gx
```

## Решение

### Шаг 2: Вывод справки
```
\?  — list of psql backslash commands
\h  — help on SQL commands
\h CREATE DATABASE — SHOW CREATE TABLE for CREATE DATABASE
```

### Шаг 5: Вывод запросов
```
           version
-----------------------------
 PostgreSQL 16.9 (Ubuntu 16.9-1.pgdg24.04+1) ...
(1 row)

  datname  |  size
-----------+--------
 postgres  | 7361 kB
 student   | 7516 kB
 template1 | 7516 kB
 template0 | 7361 kB
(4 rows)

 current_user | current_database
--------------+------------------
 postgres     | postgres
(1 row)
```

## Контрольные вопросы

1. Как переключиться на другую базу данных внутри psql?
2. Чем `\l+` отличается от `\l`?
3. Как посмотреть SQL-запрос, который выполняет команда psql (например, `\dt`)?

## Дополнительное задание

Настройте приглашение psql так, чтобы оно показывало `user@database=#`. Запишите настройку в файл `~/.psqlrc`.
