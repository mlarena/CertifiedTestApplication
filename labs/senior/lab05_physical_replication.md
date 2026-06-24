# Лабораторная работа №5: Физическая репликация

## Цель
Настроить потоковую физическую репликацию между двумя серверами, проверить синхронизацию данных.

## Теория
Физическая репликация основана на передаче журнальных записей WAL от мастера к реплике. Реплика постоянно применяет полученные записи, поддерживая актуальное состояние. Мастер → walsender, реплика → walreceiver + startup.

## Задание

### Шаг 1. Создание резервной копии для реплики

```bash
pg_basebackup \
    --pgdata=/tmp/replica_data \
    --checkpoint=fast \
    --wal-method=stream \
    -R
```

### Шаг 2. Настройка мастера

```sql
-- Проверка параметров
SELECT name, setting FROM pg_settings
WHERE name IN ('wal_level', 'max_wal_senders');

-- Просмотр разрешений в pg_hba.conf
SELECT type, database, user_name, address, auth_method
FROM pg_hba_file_rules()
WHERE 'replication' = ANY(database);
```

### Шаг 3. Развёртывание реплики

```bash
# Останавливаем второй кластер
sudo pg_ctlcluster 16 replica stop

# Заменяем данные
sudo rm -rf /var/lib/postgresql/16/replica
sudo mv /tmp/replica_data /var/lib/postgresql/16/replica
sudo chown -R postgres:postgres /var/lib/postgresql/16/replica

# Запускаем
sudo pg_ctlcluster 16 replica start
```

### Шаг 4. Проверка репликации

```sql
-- На мастере
SELECT pid, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       sync_state
FROM pg_stat_replication;

-- На реплике
SELECT pg_is_in_recovery();
```

### Шаг 5. Тестирование

```sql
-- На мастере
CREATE DATABASE replica_test;
\c replica_test
CREATE TABLE t(n integer);
INSERT INTO t VALUES (1), (2), (3);

-- На реплике (порт 5433)
\! psql -p 5433 -d replica_test -c "SELECT * FROM t;"
```

### Шаг 6. Попытка записи на реплике

```sql
-- На реплике
\! psql -p 5433 -d replica_test -c "INSERT INTO t VALUES (4);"
-- ERROR: cannot execute INSERT in a read-only transaction
```

## Решение

### Шаг 4: Результат
```
-- На мастере:
  pid  |   state    | sent_lsn  | write_lsn | flush_lsn | replay_lsn | sync_state
-------+------------+-----------+-----------+-----------+------------+------------
 25305 | streaming  | 0/3000060 | 0/3000060 | 0/3000060 | 0/3000060  | async
(1 row)

-- На реплике:
 pg_is_in_recovery
--------------------
 t
(1 row)
```

## Контрольные вопросы

1. Что такое `sync_state` и как влияет на потерю данных?
2. Зачем нужен `standby.signal`?
3. Как проверить отставание реплики от мастера?

## Дополнительное задание

Настройте синхронную репликацию и проверьте, что транзакция блокируется при остановленной реплике.
