# Лабораторная работа №7: Архивирование WAL и Point-in-Time Recovery

## Цель
Настроить файловое архивирование WAL, выполнить Point-in-Time Recovery (PITR), понять разницу между архивом и потоковым реплицированием.

## Теория
Архивирование WAL позволяет сохранять все журнальные сегменты, обеспечивая возможность восстановления на любую точку времени.

Механизм: `archive_command` копирует WAL-сегменты в архивный каталог при завершении сегмента.

PITR (Point-in-Time Recovery) позволяет восстановить базу на конкретный момент времени.

## Задание

### Шаг 1. Настройка архивирования

```bash
# Создание архивного каталога
mkdir -p /tmp/wal_archive
chmod 700 /tmp/wal_archive

# Настройка в postgresql.conf
ALTER SYSTEM SET archive_mode TO 'on';
ALTER SYSTEM SET archive_command TO 'cp %p /tmp/wal_archive/%f';
ALTER SYSTEM SET wal_level TO 'replica';
SELECT pg_reload_conf();

# Проверка
SHOW archive_mode;
SHOW archive_command;
```

### Шаг 2. Проверка архивирования

```sql
-- Принудительный переключение WAL-сегмента
SELECT pg_switch_wal();

-- Проверка архивного каталога
\! ls -lh /tmp/wal_archive/

-- Мониторинг через pg_stat_archiver
SELECT archived_count, last_archived_wal, last_archived_time
FROM pg_stat_archiver;
```

### Шаг 3. Создание базового бэкапа

```bash
# Бэкап
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/pitr_backup \
  -Fp -Xs -P

# Создание recovery-файла
cat > /tmp/pitr_backup/postgresql.auto.conf << EOF
restore_command = 'cp /tmp/wal_archive/%f %p'
recovery_target_timeline = 'latest'
EOF
```

### Шаг 4. Point-in-Time Recovery

```bash
# Добавление данных
sudo -u postgres psql -c "
CREATE DATABASE pitr_test;
\c pitr_test
CREATE TABLE t(id integer, val text);
INSERT INTO t SELECT generate_series(1, 100), 'value';
"

# Запоминаем время
psql -c "SELECT now();"
# 2025-06-23 10:30:00

# Удаляем данные
psql -c "DELETE FROM pitr_test.t;"

# Остановка сервера
sudo pg_ctlcluster 16 main stop

# Восстановление из бэкапа
cp -r /tmp/pitr_backup /var/lib/postgresql/16/main
chmod 700 /var/lib/postgresql/16/main

# Настройка recovery_target_time
cat > /var/lib/postgresql/16/main/postgresql.auto.conf << EOF
restore_command = 'cp /tmp/wal_archive/%f %p'
recovery_target_time = '2025-06-23 10:30:00'
recovery_target_action = 'promote'
EOF

# Запуск сервера
sudo pg_ctlcluster 16 main start

# Проверка
psql -c "SELECT count(*) FROM pitr_test.t;"
# Результат: 100 (данные восстановлены до DELETE)
```

### Шаг 5. Мониторинг архивирования

```sql
-- Статистика архивирования
SELECT
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time,
    stats_reset
FROM pg_stat_archiver;

-- Проверка WAL-уровня
SHOW wal_level;

-- Проверка archive_mode
SHOW archive_mode;
```

### Шаг 6. Recovery target options

```sql
-- recovery_target_name — восстановление по точке
recovery_target_name = 'my_backup'

-- recovery_target_xid — восстановление по транзакции
recovery_target_xid = '12345'

-- recovery_target_lsn — восстановление по LSN
recovery_target_lsn = '0/1A2B3C4D'

-- recovery_target_inclusive — включить/исключить целевую точку
recovery_target_inclusive = true
```

## Решение

### Шаг 2: Результат
```
 archived_count | last_archived_wal | last_archived_time
----------------+-------------------+---------------------
              1 | 000000010000000000000001 | 2025-06-23 10:30:00
```

## Контрольные вопросы

1. Что произойдёт, если archive_command вернёт ошибку?
2. Чем PITR отличается от репликации?
3. Что делает recovery_target_action?
4. Как восстановить данные после DELETE?

## Дополнительное задание

Настройте архивирование с ротацией архива и автоматическим удалением старых WAL-сегментов.