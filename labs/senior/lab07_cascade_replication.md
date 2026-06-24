# Лабораторная работа №7: Каскадная и отложенная репликация

## Цель
Изучить каскадную репликацию (реплика → реплика) и отложенную репликацию (recovery_target_lag).

## Теория
Каскадная репликация: мастер → реплика A → реплика B. Снижает нагрузку на мастер. Отложенная репликация: реплика применяет WAL с задержкой, позволяя просматривать данные в прошлом.

## Задание

### Шаг 1. Каскадная репликация

```sql
-- На мастере: разрешаем каскадную репликацию
ALTER SYSTEM SET max_wal_senders = 10;
SELECT pg_reload_conf();
```

```bash
# Создаём вторую резервную копию от реплики
pg_basebackup \
    -h localhost -p 5433 \
    --pgdata=/tmp/cascade_data \
    --checkpoint=fast \
    --wal-method=stream \
    -R

# Разворачиваем каскадную реплику
sudo mkdir -p /var/lib/postgresql/16/cascade
sudo mv /tmp/cascade_data/* /var/lib/postgresql/16/cascade/
sudo chown -R postgres:postgres /var/lib/postgresql/16/cascade

# Запускаем на отдельном порту
sudo -u postgres pg_ctl -D /var/lib/postgresql/16/cascade -o "-p 5434" start
```

### Шаг 2. Проверка каскада

```sql
-- На мастере
SELECT pid, state, application_name, sync_state
FROM pg_stat_replication;

-- На реплике (порт 5433): добавляем запись
\! psql -p 5433 -d lab_sync -c "INSERT INTO t VALUES (999);"

-- На каскадной реплике (порт 5434)
\! psql -p 5434 -d lab_sync -c "SELECT * FROM t;"
```

### Шаг 3. Отложенная репликация

```sql
-- На мастере
CREATE DATABASE lab_delayed;
ALTER SYSTEM SET max_standby_streaming_delay = '5min';
SELECT pg_reload_conf();
```

```bash
# На реплике (порт 5433): добавляем recovery.conf с задержкой
# (или через ALTER SYSTEM на реплике)
```

## Решение

### Шаг 2: Результат
```
-- На мастере:
  pid  |   state    | application_name | sync_state
-------+------------+------------------+------------
 25305 | streaming  | 16/replica       | async
 26001 | streaming  | 16/cascade       | async
(2 rows)
```

## Контрольные вопросы

1. Каков максимальный каскад реплик?
2. Как `max_standby_streaming_delay` влияет на конфликты очистки?
3. Что такое `hot_standby_feedback` и когда он нужен?

## Дополнительное задание

Настройте реплику с задержкой 10 минут и проверьте, что она показывает данные 10-минутной давности.
