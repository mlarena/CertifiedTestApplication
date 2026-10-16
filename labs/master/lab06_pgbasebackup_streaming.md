# Лабораторная работа №6: pg_basebackup — потоковое резервное копирование

## Цель
Освоить pg_basebackup: форматы (tar, plain), потоковое копирование, WAL-стриминг, checkpoint fast, инкрементальные бэкапы.

## Теория
pg_basebackup создаёт физическое резервное копирование кластера. Форматы: `tar` (сжатый архив) и `plain` (копирование файлов).

Потоковое копирование позволяет не останавливать сервер при создании бэкапа. WAL-стриминг обеспечивает консистентность.

## Задание

### Шаг 1. Базовый pg_basebackup

```bash
# Простой бэкап в plain-формате
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/base_backup \
  -Fp -Xs -P -v

# Проверка
ls -lh /tmp/base_backup/
ls -lh /tmp/base_backup/pg_wal/
```

### Шаг 2. Формат tar

```bash
# Создание tar-архива
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/base_backup.tar \
  -Ft -Xs -z -P -v

# Проверка
ls -lh /tmp/base_backup.tar
# base.tar.gz, pg_wal.tar.gz, base.tar
```

### Шаг 3. Потоковое копирование

```bash
# Потоковое копирование (Xs = stream)
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/stream_backup \
  -Fp -Xs -P

# Проверка WAL-стриминга
ls -lh /tmp/stream_backup/pg_wal/
```

### Шаг 4. Checkpoint fast

```bash
# Быстрая контрольная точка
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/fast_backup \
  -Fp -Xs -c fast -P

# Проверка лога
tail -n 5 /tmp/fast_backup/pg_stat_tmp/pg_stat.log
```

### Шаг 5. Восстановление из бэкапа

```bash
# Создание recovery-конфигурации
cat > /tmp/base_backup/postgresql.auto.conf << EOF
restore_command = 'cp /tmp/wal_archive/%f %p'
recovery_target_timeline = 'latest'
EOF

# Проверка
cat /tmp/base_backup/postgresql.auto.conf
```

### Шаг 6. Создание реплики

```bash
# Создание реплики через pg_basebackup
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/replica \
  -Fp -Xs -R -P

# Проверка
ls -lh /tmp/replica/standby.signal
cat /tmp/replica/postgresql.auto.conf
```

### Шаг 7. Мониторинг бэкапа

```bash
# Прогресс через -P
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/progress_backup \
  -Fp -Xs -P

# Вывод:
# 24442/24442 kB (100%), 1/1 tablespace
```

### Шаг 8. Исключение таблиц из бэкапа

```bash
# pg_basebackup не поддерживает --exclude
# Но можно исключить через replication slot
pg_basebackup -h localhost -p 5432 -U postgres -D /tmp/slot_backup \
  -Fp -Xs -S my_slot -P
```

## Решение

### Шаг 1: Результат
```
24442/24442 kB (100%), 1/1 tablespace
```

### Шаг 6: Результат
```
restore_command = 'cp /tmp/wal_archive/%f %p'
recovery_target_timeline = 'latest'
```

## Контрольные вопросы

1. Чем -Fp отличается от -Ft?
2. Что делает -Xs?
3. Зачем нужен -R?
4. Как создать бэкап с checkpoint fast?

## Дополнительное задание

Создайте бэкап в tar-формате со сжатием, восстановите его и настройте как реплику.