# Лабораторная работа №5: Глубокая диагностика блокировок

## Цель
Освоить глубокую диагностику блокировок: pg_locks, pg_blocking_pids, pg_stat_activity, анализ deadlock graph, advisory locks, lock_timeout.

## Теория
PostgreSQL имеет многоуровневую систему блокировок:
- Блокировки отношений (8 режимов)
- Блокировки строк (4 режима)
- Advisory-блокировки
- Предикатные блокировки
- Блокировки в оперативной памяти (LWLock, buffer pin)

## Задание

### Шаг 1. pg_locks — все блокировки

```sql
-- Все блокировки
SELECT pid, locktype, relation::regclass, mode, granted, fastpath
FROM pg_locks
ORDER BY granted, locktype;

-- Блокировки безGranted
SELECT pid, locktype, relation::regclass, mode,
       to_char(waitstart, 'HH24:MI:SS') AS wait_start
FROM pg_locks
WHERE NOT granted;

-- Сводка по режимам
SELECT mode, count(*) AS total_locks,
       count(*) FILTER (WHERE granted) AS granted,
       count(*) FILTER (WHERE NOT granted) AS waiting
FROM pg_locks
GROUP BY mode
ORDER BY total_locks DESC;
```

### Шаг 2. pg_blocking_pids — кто блокирует

```sql
-- Кто кого блокирует
SELECT
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
CROSS JOIN LATERAL pg_blocking_pids(blocked.pid) AS bpid(pid)
JOIN pg_stat_activity blocking ON blocking.pid = bpid.pid;

-- Детальная информация
SELECT
    a.pid AS waiter_pid,
    a.query AS waiter_query,
    a.wait_event_type,
    a.wait_event,
    a.wait_start,
    b.pid AS blocker_pid,
    b.query AS blocker_query,
    b.state AS blocker_state
FROM pg_stat_activity a
CROSS JOIN LATERAL pg_blocking_pids(a.pid) AS bpid(pid)
JOIN pg_stat_activity b ON b.pid = bpid.pid
WHERE a.wait_event_type = 'Lock';
```

### Шаг 3. Диаграмма блокировок

```sql
-- Поиск цепочек блокировок
WITH RECURSIVE lock_chain AS (
    -- Начальная точка: заблокированный процесс
    SELECT
        a.pid AS blocked_pid,
        a.query AS blocked_query,
        b.pid AS blocking_pid,
        b.query AS blocking_query,
        1 AS level
    FROM pg_stat_activity a
    CROSS JOIN LATERAL pg_blocking_pids(a.pid) AS bpid(pid)
    JOIN pg_stat_activity b ON b.pid = bpid.pid
    WHERE a.wait_event_type = 'Lock'
      AND a.pid = pg_backend_pid()

    UNION ALL

    -- Рекурсивное соединение
    SELECT
        a.pid,
        a.query,
        b.pid,
        b.query,
        level + 1
    FROM lock_chain lc
    JOIN pg_stat_activity a ON a.pid = lc.blocking_pid
    CROSS JOIN LATERAL pg_blocking_pids(a.pid) AS bpid(pid)
    JOIN pg_stat_activity b ON b.pid = bpid.pid
    WHERE a.wait_event_type = 'Lock'
      AND level < 10
)
SELECT * FROM lock_chain
ORDER BY level;
```

### Шаг 4. Advisory-блокировки

```sql
-- Установка advisory-блокировки
SELECT pg_advisory_lock(12345);

-- Проверка
SELECT pid, locktype, classid, objid, mode, granted
FROM pg_locks
WHERE locktype = 'advisory';

-- Отключение
SELECT pg_advisory_unlock(12345);

-- Разделяемый режим
SELECT pg_advisory_lock_shared(12345);
SELECT pg_advisory_unlock_shared(12345);
```

### Шаг 5. Deadlock-анализ

```sql
-- Настройка deadlock_timeout
SET deadlock_timeout TO '500ms';

-- Создание deadlock
-- Сеанс 1:
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2:
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Сеанс 1:
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- Ждёт 500ms...

-- Сеанс 2:
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- DEADLOCK!
```

### Шаг 6. lock_timeout

```sql
-- Таймаут ожидания блокировки
SET lock_timeout TO '3s';

-- Попытка захватить блокировку
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- Если другой сеанс удерживает блокировку:
-- ERROR: canceling statement due to lock timeout
```

### Шаг 7. Мониторинг блокировок

```sql
-- Сводка
SELECT
    locktype,
    mode,
    count(*) AS total,
    count(*) FILTER (WHERE granted) AS granted,
    count(*) FILTER (WHERE NOT granted) AS waiting,
    count(*) FILTER (WHERE NOT granted) * 100 / count(*) AS wait_pct
FROM pg_locks
GROUP BY locktype, mode
ORDER BY wait_pct DESC;
```

## Решение

### Шаг 2: Результат
```
 waiter_pid | blocker_pid | wait_event_type | wait_event
------------+-------------+-----------------+-------------
       1234 |        5678 | Lock            | relation
```

## Контрольные вопросы

1. Чем advisory-блокировки отличаются от обычных?
2. Как pg_blocking_pids работает?
3. Что произойдёт, если deadlock_timeout = 0?
4. Как определить, какая таблица больше всего блокируется?

## Дополнительное задание

Создайте скрипт мониторинга блокировок, который каждые 10 секунд сохраняет данные в таблицу для последующего анализа.