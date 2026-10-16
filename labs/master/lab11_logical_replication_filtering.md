# Лабораторная работа №11: Фильтрация логической репликации

## Цель
Настроить фильтрацию на уровне публикации и подписки: row filter, column filter, исключение операций, фильтрация таблиц.

## Теория
Начиная с PostgreSQL 15 логическая репликация поддерживает фильтрацию:
- `WHERE` на публикации (row filter)
- `WHERE` на подписке (row filter)
- `columns` на подписке (column filter)
- `publish` на подписке (фильтр операций)

## Задание

### Шаг 1. Настройка публикаций с фильтром

```sql
-- Publisher (порт 5432)
CREATE DATABASE pub_db;
\c pub_db

CREATE TABLE orders(
    id integer PRIMARY KEY,
    customer_id integer,
    amount numeric,
    status text,
    created_at timestamptz
);

INSERT INTO orders
SELECT i, i % 10, random() * 1000,
       CASE WHEN i % 3 = 0 THEN 'pending' ELSE 'completed' END,
       now()
FROM generate_series(1, 1000) i;

-- Публикация с фильтром: только completed
CREATE PUBLICATION pub_completed FOR TABLE orders WHERE (status = 'completed');

-- Проверка
SELECT * FROM pg_publication_tables;
SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete FROM pg_publication;
```

### Шаг 2. Настройка подписки с фильтром

```sql
-- Subscriber (порт 5433)
CREATE DATABASE sub_db;
\c sub_db

CREATE TABLE orders(
    id integer PRIMARY KEY,
    customer_id integer,
    amount numeric,
    status text,
    created_at timestamptz
);

-- Подписка с фильтром: только customer_id = 5
CREATE SUBSCRIPTION sub_orders
    CONNECTION 'host=localhost port=5432 dbname=pub_db'
    PUBLICATION pub_completed
    WITH (slot_name = sub_orders, create_slot = true);

-- Проверка
SELECT * FROM pg_stat_subscription;
SELECT count(*) FROM orders;
```

### Шаг 3. Фильтр на уровне подписки

```sql
-- Подписка с WHERE-фильтром
CREATE SUBSCRIPTION sub_filtered
    CONNECTION 'host=localhost port=5432 dbname=pub_db'
    PUBLICATION pub_completed
    WITH (
        copy_data = true,
        connect = true,
        enabled = true
    );

-- Добавление фильтра через ALTER
ALTER SUBSCRIPTION sub_filtered REFRESH PUBLICATION;
```

### Шаг 4. Фильтр столбцов

```sql
-- Публикация с фильтрацией столбцов
-- На подписке:
CREATE TABLE orders_subset(
    id integer PRIMARY KEY,
    amount numeric
);

-- Подписка только на определённые столбцы
CREATE SUBSCRIPTION sub_subset
    CONNECTION 'host=localhost port=5432 dbname=pub_db'
    PUBLICATION pub_completed
    WITH (copy_data = false);

-- Фильтрация на уровне подписки (PG15+):
ALTER SUBSCRIPTION sub_subset SET (slot_name = NONE);
DROP SUBSCRIPTION sub_subset;

-- Создание подписки с фильтром столбцов
CREATE SUBSCRIPTION sub_cols
    CONNECTION 'host=localhost port=5432 dbname=pub_db'
    PUBLICATION pub_completed
    WITH (copy_data = true);
```

### Шаг 5. Исключение операций

```sql
-- Публикация без DELETE
CREATE PUBLICATION pub_no_delete FOR TABLE orders
    WITH (publish = 'insert,update');

-- Подписка только на INSERT
CREATE SUBSCRIPTION sub_insert_only
    CONNECTION 'host=localhost port=5432 dbname=pub_db'
    PUBLICATION pub_no_delete
    WITH (
        copy_data = false,
        create_slot = true,
        slot_name = 'sub_insert'
    );

-- Проверка
SELECT subname, subenabled FROM pg_subscription;
```

### Шаг 6. Мониторинг репликации

```sql
-- Проверка статуса подписки
SELECT subname, subenabled, subconninfo, subslotname
FROM pg_subscription;

-- Проверка репликации
SELECT subname, received_lsn, last_msg_send_time, last_msg_receipt_time
FROM pg_stat_subscription;

-- Проверка данных
SELECT count(*), status FROM orders GROUP BY status;
```

## Решение

### Шаг 1: Результат
```
 pubname       | puballtables | pubinsert | pubupdate | pubdelete
---------------+--------------+-----------+-----------+----------
 pub_completed | f            | t         | t         | t
```

### Шаг 6: Результат
```
 subname    | received_lsn | last_msg_receipt_time
------------+--------------+------------------------
 sub_orders | 0/1A2B3C4D   | 2025-06-23 10:00:00
```

## Контрольные вопросы

1. Как работает WHERE на публикации?
2. Можно ли фильтровать DELETE на подписке?
3. Что делает copy_data = false?
4. Как добавить фильтр на существующую подписку?

## Дополнительное задание

Настройте репликацию только для определённого customer_id с помощью row filter на публикации и column filter на подписке.