# Лабораторная работа №1: Логическое резервное копирование (pg_dump)

## Цель
Освоить утилиту pg_dump: создание резервных копий в различных форматах, фильтрация объектов, параллельный режим.

## Теория
`pg_dump` создаёт логическую резервную копию базы данных — набор команд SQL или файл в специальном формате. Преимущества: можно копировать отдельные объекты, восстанавливать на другой версии СУБД. Недостаток: медленное восстановление для больших баз.

Форматы: `plain` (SQL-скрипт), `custom` (сжатый, с оглавлением), `directory` (параллельный), `tar`.

## Задание

### Шаг 1. Создание тестовой базы

```sql
CREATE DATABASE lab_backup;
\c lab_backup

CREATE TABLE products(id integer PRIMARY KEY, name text, price numeric);
INSERT INTO products SELECT id, md5(id::text), random()*1000
FROM generate_series(1, 10000);

CREATE INDEX idx_prod_name ON products(name);
```

### Шаг 2. pg_dump в формате plain

```bash
pg_dump -d lab_backup > /tmp/lab_backup_plain.sql
head -30 /tmp/lab_backup_plain.sql
```

### Шаг 3. pg_dump в формате custom

```bash
pg_dump -d lab_backup -Fc -f /tmp/lab_backup_custom.dump
ls -lh /tmp/lab_backup_custom.dump
```

### Шаг 4. pg_dump в формате directory (параллельный)

```bash
mkdir -p /tmp/lab_backup_dir
pg_dump -d lab_backup -Fd -j 2 -f /tmp/lab_backup_dir
ls -lh /tmp/lab_backup_dir/
```

### Шаг 5. Экспорт конкретной таблицы

```bash
pg_dump -d lab_backup -t products -Fc -f /tmp/products.dump
```

### Шаг 6. Экспорт только данных

```bash
pg_dump -d lab_backup -t products --data-only -Fc -f /tmp/products_data.dump
```

### Шаг 7. Экспорт только схемы

```bash
pg_dump -d lab_backup --schema-only -Fc -f /tmp/products_schema.dump
```

### Шаг 8. Копирование таблицы через pipe

```sql
CREATE DATABASE lab_backup2;
```

```bash
pg_dump -d lab_backup -t products | psql -d lab_backup2
```

## Решение

### Шаг 2: Результат
```
--
-- PostgreSQL database dump
--
-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9
SET statement_timeout = 0;
SET lock_timeout = 0;
...
CREATE TABLE public.products (
    id integer NOT NULL,
    name text,
    price numeric
);
```

### Шаг 4: Результат
```
-rw-r--r-- 1 student student 128K Jun 23 23:50 16386.dump
-rw-r--r-- 1 student student  64K Jun 23 23:50 16386.dump.gz
drwxr-xr-x 1 student student 4.0K Jun 23 23:50 pg_dump.info
```

## Контрольные вопросы

1. Какой формат лучше использовать для параллельного восстановления?
2. Чем `--data-only` отличается от `--schema-only`?
3. Почему при восстановлении из pg_dump нужно создавать БД из template0?

## Дополнительное задание

Создайте резервную копию всех пользовательских объектов (кроме индексов) и восстановите её.
