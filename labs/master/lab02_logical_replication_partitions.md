# Лабораторная работа №2: Логическая репликация с партициями

## Цель
Настроить логическую репликацию партиционированных таблиц, понять особенности репликации партиций, обработку конфликтов.

## Теория
Логическая репликация PostgreSQL реплицирует таблицы через публикации (publication) и подписки (subscription). Для партиционированных таблиц репликация работает на уровне партиций, а не родительской таблицы.

## Задание

### Шаг 1. Создание партиционированной таблицы на publisher

```sql
-- Publisher (порт 5432)
CREATE DATABASE pub_db;
\c pub_db

CREATE TABLE events(
    id bigint GENERATED ALWAYS AS IDENTITY,
    event_date date NOT NULL,
    event_type text NOT NULL,
    payload jsonb
) PARTITION BY RANGE (event_date);

CREATE TABLE events_2025q1 PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE events_2025q2 PARTITION OF events
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');

-- Тестовые данные
INSERT INTO events(event_date, event_type, payload)
SELECT '2025-01-01'::date + (i % 180), 'click', jsonb_build_object('n', i)
FROM generate_series(1, 1000) i;
```

### Шаг 2. Создание публикации

```sql
-- Публикация всех партиций
CREATE PUBLICATION pub_events FOR TABLE events;

-- Или только определённые партиции
CREATE PUBLICATION pub_events_q1 FOR TABLE events_2025q1;

-- Проверка
SELECT * FROM pg_publication_tables;
```

### Шаг 3. Настройка subscriber

```sql
-- Subscriber (порт 5433)
CREATE DATABASE sub_db;
\c sub_db

-- Создаём такую же партиционированную структуру
CREATE TABLE events(
    id bigint GENERATED ALWAYS AS IDENTITY,
    event_date date NOT NULL,
    event_type text NOT NULL,
    payload jsonb
) PARTITION BY RANGE (event_date);

CREATE TABLE events_2025q1 PARTITION OF events
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE events_2025q2 PARTITION OF events
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
```

### Шаг 4. Создание подписки

```sql
-- Подписка на все партиции
CREATE SUBSCRIPTION sub_events
    CONNECTION 'host=localhost port=5432 dbname=pub_db'
    PUBLICATION pub_events
    WITH (copy_data = true);

-- Проверка
SELECT * FROM pg_subscription;
SELECT * FROM pg_stat_subscription;
```

### Шаг 5. Добавление новой партиции

```sql
-- Publisher: добавляем новую партицию
CREATE TABLE events_2025q3 PARTITION OF events
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');

-- Публикация не обновляется автоматически!
-- Нужно явно добавить в публикацию
ALTER PUBLICATION pub_events ADD TABLE events_2025q3;

-- Subscriber: создаём партицию и подписываем
CREATE TABLE events_2025q3 PARTITION OF events
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');

-- Подписка на новую партицию
ALTER SUBSCRIPTION sub_events REFRESH PUBLICATION;
```

### Шаг 6. Мониторинг репликации

```sql
-- Статус подписки
SELECT subname, subenabled, subconninfo, subslotname
FROM pg_subscription;

-- Отставание репликации
SELECT subname, received_lsn, last_msg_send_time, last_msg_receipt_time
FROM pg_stat_subscription;

-- Задержки
SELECT subname,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), received_lsn)) AS lag
FROM pg_stat_subscription;
```

### Шаг 7. Конфликты и обработка

```sql
-- Конфликт: на subscriber уже есть данные
-- Вариант 1: пересоздать подписку с copy_data = false
-- Вариант 2: использовать origin = none (для двухсторонней репликации)

-- Проверка конфликтов
SELECT * FROM pg_subscription_rel;
```

## Решение

### Шаг 4: Результат
```
 subname    | subenabled | subconninfo
------------+------------+----------------------------------
 sub_events | t          | host=localhost port=5432 dbname=...
```

### Шаг 6: Результат
```
 subname    | received_lsn | lag
------------+--------------+-----
 sub_events | 0/1A2B3C4D   | 0 bytes
```

## Контрольные вопросы

1. Реплицируется ли родительская таблица или партиции?
2. Что произойдёт при вставке данных в таблицу на subscriber?
3. Как добавить новую партицию в существующую подписку?
4. Что делает `copy_data = true`?

## Дополнительное задание

Настройте двухстороннюю репликацию партиционированной таблицы с `origin = none` и проверьте разрешение конфликтов.