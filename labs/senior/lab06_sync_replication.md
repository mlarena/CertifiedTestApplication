# Лабораторная работа №6: Синхронная репликация

## Цель
Настроить синхронную физическую репликацию, проверить гарантии доставки данных, изучить поведение при сбое реплики.

## Теорция
При синхронной репликации фиксация транзакции не завершается до подтверждения приёма WAL-записей синхронной репликой. Это обеспечивает потерю 0 данных при сбое мастера, но снижает производительность.

## Задание

### Шаг 1. Проверка текущего режима

```sql
SHOW synchronous_commit;
SHOW synchronous_standby_names;
```

### Шаг 2. Настройка синхронной репликации

```sql
-- На мастере: имя кластера реплики
SHOW cluster_name;

-- Установка
ALTER SYSTEM SET synchronous_standby_names = '"16/replica"';
SELECT pg_reload_conf();

-- Проверка
SELECT sync_state FROM pg_stat_replication;
```

### Шаг 3. Тестирование блокировки

```sql
-- На мастере
CREATE DATABASE lab_sync;
\c lab_sync
CREATE TABLE t(n integer);

-- Останавливаем реплику
\! sudo pg_ctlcluster 16 replica stop

-- Пытаемся выполнить транзакцию (блокируется!)
BEGIN;
INSERT INTO t VALUES (1);
-- Ожидание...

-- Запускаем реплику
\! sudo pg_ctlcluster 16 replica start
-- Транзакция завершается
COMMIT;
```

### Шаг 4. Проверка данных

```sql
-- На мастере
SELECT * FROM t;

-- На реплике
\! psql -p 5433 -d lab_sync -c "SELECT * FROM t;"
```

### Шаг 5. Отключение синхронной репликации

```sql
ALTER SYSTEM RESET synchronous_standby_names;
SELECT pg_reload_conf();
```

## Решение

### Шаг 2: Результат
```
SHOW synchronous_standby_names;
 synchronous_standby_names
----------------------------
 "16/replica"
(1 row)

SELECT sync_state FROM pg_stat_replication;
 sync_state
------------
 sync
(1 row)
```

## Контрольные вопросы

1. Как `synchronous_commit` влияет на производительность?
2. Что такое `remote_apply` и когда нужно?
3. Как настроить синхронную репликацию с приоритетом?

## Дополнительное задание

Настройте `synchronous_commit = remote_apply` и проверьте, что данные видны на реплике сразу после COMMIT.
