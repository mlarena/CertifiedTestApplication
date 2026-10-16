# Лабораторная работа №17: Диагностика блокировок

## Цель
Научиться диагностировать блокировки: pg_locks, pg_blocking_pids, NOWAIT, SKIP LOCKED, lock_timeout, deadlock_timeout.

## Теория
PostgreSQL использует многоуровневую систему блокировок: отношения (8 режимов), строки (4 режима), ресурсы памяти (спин-блокировки, лёгкие блокировки, buffer pin).

`pg_locks` показывает все текущие блокировки. `pg_blocking_pids()` возвращает PID процессов, которые мешают данному получить блокировку.

`NOWAIT` и `SKIP LOCKED` позволяют не ждать блокировку. `lock_timeout` и `deadlock_timeout` задают предельное время ожидания.

## Задание

### Шаг 1. pg_locks и pg_blocking_pids

```sql
CREATE DATABASE lab_locks;
\c lab_locks

CREATE TABLE accounts(id integer PRIMARY KEY, balance numeric);
INSERT INTO accounts VALUES (1, 1000), (2, 2000);
```

```sql
-- Сеанс 1: BEGIN + UPDATE
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2: SELECT FOR UPDATE — блокируется
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- Сеанс 3: мониторинг
SELECT pid, locktype, relation::regclass, mode, granted
FROM pg_locks
WHERE NOT granted;

-- pg_blocking_pids
SELECT pid, pg_blocking_pids(pid) AS blocked_by
FROM pg_locks
WHERE NOT granted;

-- pg_stat_activity
SELECT pid, state, query, wait_event_type, wait_event,
       pg_blocking_pids(pid) AS blocked_by
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

### Шаг 2. NOWAIT — без ожидания

```sql
-- Сеанс 1: BEGIN + UPDATE
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2: SELECT FOR UPDATE NOWAIT — ошибка
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row in relation "accounts"

-- COMMIT в сеансе 1
COMMIT;
```

### Шаг 3. SKIP LOCKED — пропуск заблокированных

```sql
-- Сеанс 1: BEGIN + UPDATE
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2: SELECT FOR UPDATE SKIP LOCKED — пропускает id=1
BEGIN;
SELECT * FROM accounts WHERE id IN (1, 2) FOR UPDATE SKIP LOCKED;
-- Возвращает только id=2
```

### Шаг 4. lock_timeout

```sql
-- Сеанс 1: BEGIN + UPDATE
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2: lock_timeout = 2s
SET lock_timeout TO '2s';
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Ждёт 2 секунды, затем:
-- ERROR: canceling statement due to lock timeout
```

### Шаг 5. deadlock_timeout и взаимоблокировки

```sql
-- Сеанс 1: BEGIN + UPDATE id=1
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2: BEGIN + UPDATE id=2
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Сеанс 1: UPDATE id=2 — ждёт deadlock_timeout
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Сеанс 2: UPDATE id=1 — deadlock!
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- ERROR: deadlock detected
-- DETAIL: Process 1234 waits for ShareLock on transaction 5678; blocked by process 5679.

-- Проверка deadlock_timeout
SHOW deadlock_timeout;
```

### Шаг 6. pgrowlocks — блокировки строк

```sql
CREATE EXTENSION pgrowlocks;

-- Сеанс 1: BEGIN + UPDATE id=1
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Сеанс 2: pgrowlocks
SELECT locked_row, locker, multi, xids, modes, pids
FROM pgrowlocks('accounts');
-- locked_row: (0,1) — ctid
-- modes: {Update}
```

### Шаг 7. pg_locks — все типы блокировок

```sql
-- Текущие блокировки
SELECT locktype, database::regclass, relation::regclass,
       page, tuple, transactionid, virtualxid,
       mode, granted, fastpath
FROM pg_locks
ORDER BY locktype;

-- Блокировки advisory
SELECT locktype, classid, objid, mode, granted
FROM pg_locks
WHERE locktype = 'advisory';
```

## Решение

### Шаг 2: Результат
```
ERROR:  could not obtain lock on row in relation "accounts"
```

### Шаг 5: Результат
```
ERROR:  deadlock detected
DETAIL:  Process 1234 waits for ShareLock on transaction 5678; blocked by process 5679.
```

## Контрольные вопросы

1. Чем NOWAIT отличается от SKIP LOCKED?
2. Что произойдёт, если deadlock_timeout = 0?
3. Как pgrowlocks показывает мультитранзакции?
4. Как отличить блокировку отношения от блокировки строки в pg_locks?

## Дополнительное задание

Создайте скрипт, который периодически опрашивает pg_locks и pg_stat_activity, и выводит все транзакции, ожидающие блокировку дольше 5 секунд.