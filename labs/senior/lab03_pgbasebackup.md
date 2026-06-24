# Лабораторная работа №3: pg_basebackup

## Цель
Освоить создание автономных физических резервных копий с помощью pg_basebackup, понять разницу между различными методами WAL.

## Теория
`pg_basebackup` подключается к серверу по протоколу репликации, выполняет контрольную точку и копирует файлы кластера. Ключи: `--wal-method=stream` (WAL включён), `--checkpoint=fast` (быстрая КТ), `-R` (настройки для реплики).

## Задание

### Шаг 1. Проверка настроек

```sql
SELECT name, setting FROM pg_settings
WHERE name IN ('wal_level', 'max_wal_senders');
```

### Шаг 2. Автономная копия (с WAL)

```bash
mkdir -p /tmp/basebackup

pg_basebackup \
    --pgdata=/tmp/basebackup \
    --checkpoint=fast \
    --wal-method=stream \
    --progress \
    --verbose
```

### Шаг 3. Проверка содержимого

```bash
ls -la /tmp/basebackup/
ls -la /tmp/basebackup/pg_wal/
cat /tmp/basebackup/backup_label
```

### Шаг 4. Копия без WAL (для архива)

```bash
mkdir -p /tmp/basebackup_no_wal

pg_basebackup \
    --pgdata=/tmp/basebackup_no_wal \
    --checkpoint=fast \
    --wal-method=none
```

### Шаг 5. Копия для реплики (-R)

```bash
mkdir -p /tmp/replica_backup

pg_basebackup \
    --pgdata=/tmp/replica_backup \
    --checkpoint=fast \
    --wal-method=stream \
    -R

# Проверяем auto.conf и standby.signal
cat /tmp/replica_backup/postgresql.auto.conf
ls -la /tmp/replica_backup/standby.signal
```

### Шаг 6. Восстановление копии

```sql
-- Второй кластер уже создан, проверяем
SELECT pg_lsclusters;
```

```bash
# Если кластер replica работает, останавливаем
sudo pg_ctlcluster 16 replica stop

# Заменяем данные
sudo rm -rf /var/lib/postgresql/16/replica
sudo mv /tmp/basebackup /var/lib/postgresql/16/replica
sudo chown -R postgres:postgres /var/lib/postgresql/16/replica

# Запускаем
sudo pg_ctlcluster 16 replica start
```

### Шаг 7. Проверка восстановления

```sql
-- На восстановленном сервере
\! psql -p 5433 -c "SELECT count(*) FROM products;"
```

## Решение

### Шаг 2: Результат
```
NOTICE: pg_basebackup: starting base backup, waiting for checkpoint to complete
pg_basebackup: checkpoint completed
pg_basebackup: transaction log start point: 0/3000060 on timeline 1
pg_basebackup: starting background wal receiver
pg_basebackup: created temporary replication slot "pg_basebackup_12345"
NOTICE: pg_basebackup: done, wrote 443 files
```

## Контрольные вопросы

1. Зачем нужен `--checkpoint=fast` при создании копии?
2. Что такое `backup_label` и зачем он нужен?
3. Как `--wal-method=stream` отличается от `--wal-method=fetch`?

## Дополнительное задание

Создайте копию через `--wal-method=send` и проверьте, что сегменты WAL копируются по мере заполнения.
