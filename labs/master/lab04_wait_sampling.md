# Лабораторная работа №4: Анализ ожиданий через pg_wait_sampling

## Цель
Изучить механизм ожидания процессов PostgreSQL: wait_event_type, wait_event, pg_wait_sampling, анализ производительности через семплирование.

## Теория
PostgreSQL отслеживает ожидания процессов через систему wait events. Каждый процесс может находиться в ожидании определённого типа: Lock, LWLock, BufferPin, IO, IPC, Client, Extension, Activity, Timeout.

`pg_wait_sampling` — расширение от PostgreSQL Pro, которое собирает статистику ожиданий через семплирование, позволяя анализировать узкие места производительности.

## Задание

### Шаг 1. Текущие ожидания

```sql
-- Все ожидания
SELECT pid, wait_event_type, wait_event, query, state
FROM pg_stat_activity
WHERE wait_event_type IS NOT NULL;

-- Типы ожиданий
SELECT wait_event_type, count(*) AS processes
FROM pg_stat_activity
WHERE wait_event_type IS NOT NULL
GROUP BY wait_event_type
ORDER BY processes DESC;
```

### Шаг 2. Типы wait_event_type

```sql
-- Все типы
SELECT DISTINCT wait_event_type FROM pg_stat_activity ORDER BY 1;

-- Lock — ожидание блокировки
SELECT pid, wait_event_type, wait_event, query, state
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

-- LWLock — лёгкая блокировка
SELECT pid, wait_event_type, wait_event, query, state
FROM pg_stat_activity
WHERE wait_event_type = 'LWLock';

-- BufferPin — закрепление буфера
SELECT pid, wait_event_type, wait_event, query, state
FROM pg_stat_activity
WHERE wait_event_type = 'BufferPin';

-- IO — ввод-вывод
SELECT pid, wait_event_type, wait_event, query, state
FROM pg_stat_activity
WHERE wait_event_type = 'IO';

-- Activity — фоновые процессы
SELECT pid, wait_event_type, wait_event, query, state
FROM pg_stat_activity
WHERE wait_event_type = 'Activity';
```

### Шаг 3. Установка pg_wait_sampling

```sql
-- Установка расширения
CREATE EXTENSION IF NOT EXISTS pg_wait_sampling;

-- Проверка
SELECT * FROM pg_available_extensions WHERE name = 'pg_wait_sampling';
```

### Шаг 4. Сбор статистики ожиданий

```sql
-- Текущие ожидания
SELECT * FROM pg_wait_sampling_current();

-- Наивысшие ожидания за сессию
SELECT * FROM pg_wait_sampling_history(100);
-- Последнее ожидание каждого процесса за сессию

-- Наивысшие ожидания
SELECT * FROM pg_wait_sampling_history(100, 1);
-- Один раз на процесс
```

### Шаг 5. Анализ ожиданий

```sql
-- Статистика ожиданий по типам
SELECT wait_event_type, wait_event, count(*) AS count
FROM pg_wait_sampling_history(1000)
GROUP BY wait_event_type, wait_event
ORDER BY count DESC;

-- Ожидания по таблицам
SELECT relation::regclass, wait_event, count(*) AS count
FROM pg_wait_sampling_history(1000)
WHERE relation IS NOT NULL
GROUP BY relation, wait_event
ORDER BY count DESC
LIMIT 20;
```

### Шаг 6. Создание сценария ожиданий

```sql
-- Создаём таблицу для теста
CREATE TABLE wait_test(id integer PRIMARY KEY, val text);
INSERT INTO wait_test SELECT generate_series(1, 10000), 'val';

-- Сеанс 1: блокирует строку
BEGIN;
UPDATE wait_test SET val = 'blocked' WHERE id = 1;

-- Сеанс 2: ждёт блокировку
-- BEGIN;
-- UPDATE wait_test SET val = 'waiting' WHERE id = 1;

-- Анализ в сеансе 3
SELECT pid, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';

-- pg_wait_sampling
SELECT * FROM pg_wait_sampling_current();
```

### Шаг 7. Сводная статистика

```sql
-- Сводка по всем типам ожиданий
SELECT
    wait_event_type,
    wait_event,
    count(*) AS total_waits,
    round(avg(wait_duration), 3) AS avg_duration_ms
FROM pg_wait_sampling_history(10000)
GROUP BY wait_event_type, wait_event
ORDER BY total_waits DESC
LIMIT 20;
```

## Решение

### Шаг 4: Результат
```
 pid  | wait_event_type | wait_event      | relation
------+-----------------+-----------------+----------
 1234 | Lock            | relation        | 16384/16390
 5678 | LWLock          | WALBufMapping   |
```

## Контрольные вопросы

1. Чем Lock отличается от LWLock?
2. Что такое Buffer Pin и как он влияет на производительность?
3. Как pg_wait_sampling собирает статистику?
4. Что означает пустой wait_event?

## Дополнительное задание

Напишите скрипт мониторинга, который каждые 5 секунд опрашивает pg_stat_activity и pg_wait_sampling, и выводит топ-5 ожидающих процессов.