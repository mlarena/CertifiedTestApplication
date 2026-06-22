# Лабораторная работа №13: Мониторинг — основы

## Цель
Освоить базовые инструменты мониторинга: `pg_stat_activity`, журнал сообщений сервера, параметры логирования.

## Теория
PostgreSQL предоставляет два основных источника информации: накопительную статистику (представления `pg_stat_*`) и журнал сообщений сервера. `pg_stat_activity` показывает текущие активности всех обслуживающих процессов.

Для настройки журнала используются параметры: `log_destination`, `logging_collector`, `log_directory`, `log_filename`, `log_min_duration_statement`.

## Задание

### Шаг 1. Текущие активности

```sql
CREATE DATABASE lab_monitoring;
\c lab_monitoring

-- Все активные сеансы
SELECT pid, usename, datname, state, query, backend_type
FROM pg_stat_activity
WHERE backend_type = 'client backend';
```

### Шаг 2. Симуляция блокировки

```sql
-- Сеанс 1
BEGIN;
CREATE TABLE t(n integer);
INSERT INTO t VALUES (42);
UPDATE t SET n = 100;
-- Не коммитим!

-- Сеанс 2
BEGIN;
UPDATE t SET n = 200;
-- Ждёт блокировку!
```

```sql
-- Сеанс 1: кто блокирует?
SELECT pid, state, wait_event, wait_event_type
FROM pg_stat_activity
WHERE backend_type = 'client backend';
```

### Шаг 3. Нахождение блокирующего процесса

```sql
-- Функция pg_blocking_pids
SELECT pid, query, pg_blocking_pids(pid) AS blocking_pids
FROM pg_stat_activity
WHERE backend_type = 'client backend'
AND cardinality(pg_blocking_pids(pid)) > 0;
```

### Шаг 4. Завершение блокирующего процесса

```sql
-- Завершаем блокирующий сеанс
SELECT pg_terminate_backend(<PID_блокирующего_процесса>);

-- Сеанс 2 разблокируется и выполняет UPDATE
```

### Шаг 5. Настройка журнала

```sql
-- Включаем логирование всех запросов
ALTER SYSTEM SET log_min_duration_statement = 0;
SELECT pg_reload_conf();

-- Выполняем запрос
SELECT sum(random()) FROM generate_series(1, 100000);

-- Проверяем журнал
\! tail -n 5 /var/log/postgresql/postgresql-16-main.log

-- Сбрасываем настройку
ALTER SYSTEM RESET log_min_duration_statement;
SELECT pg_reload_conf();
```

## Решение

### Шаг 1: Результат
```
  pid  | usename | datname    | state  | query         | backend_type
-------+---------+------------+--------+---------------+--------------
 20272 | student | lab_monitoring | active | SELECT ... | client backend
(1 row)
```

### Шаг 3: Результат
```
  pid  |       query        | blocking_pids
-------+--------------------+---------------
 20361 | UPDATE t SET n = 200 | {20272}
(1 row)
```

## Контрольные вопросы

1. Что такое `idle in transaction` и почему это проблема?
2. Какой параметр позволяет автоматически завершать долгие транзакции?
3. Чем `pg_cancel_backend` отличается от `pg_terminate_backend`?

## Дополнительное задание

Настройте `idle_in_transaction_session_timeout = 30s` и проверьте, что долгая транзакция автоматически завершается.
