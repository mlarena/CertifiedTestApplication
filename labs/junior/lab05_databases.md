# Лабораторная работа №5: Базы данных

## Цель
Научиться создавать, управлять и удалять базы данных, понимать механизм шаблонов (template0, template1), измерять размеры.

## Теория
PostgreSQL поддерживает несколько баз данных в рамках одного кластера. При инициализации создаются три шаблона: `postgres` (подключение по умолчанию), `template1` (шаблон для новых БД) и `template0` (неизменяемый шаблон для восстановления и создания БД с другой кодировкой).

Новая база данных всегда клонируется из существующей. По умолчанию используется `template1`.

## Задание

### Шаг 1. Создание базы данных

```sql
CREATE DATABASE lab_databases;
\c lab_databases
```

### Шаг 2. Проверка размера

```sql
SELECT pg_size_pretty(pg_database_size('lab_databases')) AS size;
```

### Шаг 3. Создание БД из шаблона template0

```sql
CREATE DATABASE lab_databases2 TEMPLATE template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';
\l+ lab_databases2
```

### Шаг 4. Переименование БД

```sql
\c postgres
ALTER DATABASE lab_databases RENAME TO lab_renamed;
```

### Шаг 5. Ограничение подключений

```sql
ALTER DATABASE lab_renamed CONNECTION LIMIT 5;
```

### Шаг 6. Установка параметров для БД

```sql
ALTER DATABASE lab_renamed SET work_mem = '16MB';
\drds
```

### Шаг 7. Удаление БД

```sql
DROP DATABASE lab_renamed;
DROP DATABASE lab_databases2;
DROP DATABASE lab_databases;
\l
```

## Решение

### Шаг 2: Результат
```
   size
----------
 7548 kB
(1 row)
```

### Шаг 6: Результат
```
       List of settings
 Role |    Database    |      Settings
------+----------------+-------------------
      | lab_renamed    | work_mem=16MB
(1 row)
```

## Контрольные вопросы

1. Почему БД всегда клонируется, а не создаётся с нуля?
2. Чем template0 отличается от template1?
3. Можно ли удалить БД, к которой подключены другие сеансы?

## Дополнительное задание

Создайте БД, установите для неё `search_path = public, app` через `ALTER DATABASE` и проверьте, что при переподключении путь поиска устанавливается автоматически.
