# Лабораторная работа №15: Полный DBA-сценарий

## Цель
Выполнить полный цикл работы DBA: мониторинг → диагностика → оптимизация → бэкап → восстановление.

## Теория
DBA (Database Administrator) отвечает за:
- Мониторинг и диагностику производительности
- Настройку и оптимизацию конфигурации
- Резервное копирование и восстановление
- Безопасность и управление доступом

## Задание

### Шаг 1. Мониторинг и диагностика

```sql
-- Текущие запросы
SELECT pid, state, query, wait_event_type, wait_event, query_start
FROM pg_stat_activity
ORDER BY query_start;

-- Долгие запросы
SELECT pid, query, now() - query_start AS duration
FROM pg_stat_activity
WHERE now() - query_start > interval '1 second'
ORDER BY query_start;

-- Блокировки
SELECT blocked.pid AS blocked_pid, blocking.pid AS blocking_pid
FROM pg_stat_activity blocked
CROSS JOIN LATERAL pg_blocking_pids(blocked.pid) AS bpid(pid)
JOIN pg_stat_activity blocking ON blocking.pid = bpid.pid;

-- Использование диска
SELECT relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;

-- Состояние таблиц
SELECT relname, n_dead_tup, n_live_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Шаг 2. Оптимизация конфигурации

```sql
-- Настройка параметров
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '32MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET effective_cache_size = '768MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET wal_buffers = '16MB';

-- Перезагрузка
SELECT pg_reload_conf();

-- Проверка
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
```

### Шаг 3. Оптимизация VACUUM

```sql
-- Таблицы, требующие VACUUM
SELECT relname, n_dead_tup, n_live_tup,
       n_dead_tup::float / nullif(n_live_tup + n_dead_tup, 0) * 100 AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Запуск VACUUM ANALYZE
VACUUM (VERBOSE, ANALYZE) big_table;

-- Настройка автоочистки
ALTER TABLE big_table SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_analyze_scale_factor = 0.02
);
```

### Шаг 4. Резервное копирование

```bash
# Создание бэкапа
mkdir -p /tmp/full_backup
pg_dump -d lab_dba -Fd -j 4 -f /tmp/full_backup

# Глобальные объекты
pg_dumpall --globals-only -f /tmp/globals.sql

# Проверка
ls -lh /tmp/full_backup/
ls -lh /tmp/globals.sql
```

### Шаг 5. Восстановление

```bash
# Создание новой базы
psql -c "CREATE DATABASE lab_dba_recovered;"

# Восстановление
pg_restore -d lab_dba_recovered -j 4 /tmp/full_backup/

# Проверка
psql -d lab_dba_recovered -c "SELECT count(*) FROM big_table;"
```

### Шаг 6. Безопасность

```sql
-- Создание ролей
CREATE ROLE readonly_user LOGIN;
GRANT CONNECT ON DATABASE lab_dba TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Проверка
SELECT rolname FROM pg_roles WHERE rolname = 'readonly_user';

-- Revocation
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM readonly_user;
```

### Шаг 7. Отчётность

```sql
-- Сводный отчёт
SELECT
    current_database() AS database,
    (SELECT count(*) FROM pg_stat_activity) AS active_connections,
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle in transaction') AS idle_in_tx,
    (SELECT sum(pg_database_size(datname)) FROM pg_database) AS total_size,
    (SELECT count(*) FROM pg_extension) AS extensions;

-- Прогноз роста
SELECT
    relname,
    pg_size_pretty(pg_relation_size(oid)) AS size,
    reltuples AS estimated_rows
FROM pg_class
WHERE relkind = 'r'
ORDER BY pg_relation_size(oid) DESC
LIMIT 10;
```

### Шаг 8. Автоматизация

```bash
# Создание скрипта мониторинга
cat > /tmp/dba_monitor.sh << 'EOF'
#!/bin/bash
# DBA Monitoring Script

# Проверка доступности
pg_isready -h localhost -p 5432

# Долгие запросы
psql -c "SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity WHERE now() - query_start > interval '1 second' ORDER BY duration DESC LIMIT 10;"

# Блокировки
psql -c "SELECT blocked.pid, blocking.pid FROM pg_stat_activity blocked CROSS JOIN LATERAL pg_blocking_pids(blocked.pid) AS bpid(pid) JOIN pg_stat_activity blocking ON blocking.pid = bpid.pid WHERE blocked.wait_event_type = 'Lock';"

# Мёртвые версии
psql -c "SELECT relname, n_dead_tup FROM pg_stat_user_tables WHERE n_dead_tup > 10000 ORDER BY n_dead_tup DESC;"

# Место на диске
psql -c "SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname)) FROM pg_tablespace;"
EOF

chmod +x /tmp/dba_monitor.sh
/tmp/dba_monitor.sh
```

## Решение

### Шаг 1: Результат
```
 pid  | state  | query                          | wait_event_type | wait_event
------+--------+--------------------------------+-----------------+-----------
 1234 | active | SELECT * FROM big_table        | IO              | DataFileRead
 5678 | idle   |                                |                 |
```

### Шаг 4: Результат
```
16386.dump
16386.dump.gz
pg_dump.info
```

## Контрольные вопросы

1. Какие метрики вы отслеживаете в первую очередь?
2. Как оптимизировать производительность?
3. Какое восстановление быстрее: полное или частичное?
4. Как автоматизировать мониторинг?

## Дополнительное задание

Создайте дашборд (через Grafana + pg_exporter) для мониторинга всех параметров, изученных в этом курсе.