# Лабораторная работа №14: Автоматизация бэкапов

## Цель
Научиться автоматизировать резервное копирование: создание скриптов, ротация WAL, планирование через cron.

## Теория
Автоматизация бэкапов включает: (1) регулярное создание базовых копий через pg_basebackup, (2) настройку архивации WAL, (3) ротацию старых копий, (4) мониторинг успешности.

## Задание

### Шаг 1. Создание скрипта бэкапа

```bash
cat > /tmp/backup_script.sh << 'EOF'
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/var/lib/postgresql/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/base_${DATE}"

mkdir -p "${BACKUP_DIR}"

pg_basebackup \
    --pgdata="${BACKUP_PATH}" \
    --checkpoint=fast \
    --wal-method=stream \
    --compress=zstd \
    --label="backup_${DATE}"

# Удаляем backups старше 7 дней
find "${BACKUP_DIR}" -name "base_*" -mtime +7 -exec rm -rf {} \;

echo "Backup completed: ${BACKUP_PATH}"
EOF

chmod +x /tmp/backup_script.sh
```

### Шаг 2. Тестирование скрипта

```bash
/tmp/backup_script.sh
ls -la /var/lib/postgresql/backups/
```

### Шаг 3. Настройка архивации WAL

```sql
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'cp %p /var/lib/postgresql/archive/%f';
ALTER SYSTEM SET archive_timeout = 300;  -- 5 минут
```

### Шаг 4. Настройка cron

```bash
# Просмотр текущих заданий crontab
crontab -l 2>/dev/null || echo "no crontab"

# Добавляем задание (ежедневно в 2:00)
echo "0 2 * * * /tmp/backup_script.sh >> /var/log/pg_backup.log 2>&1" | crontab -

# Проверяем
crontab -l
```

### Шаг 5. Мониторинг архивации

```sql
-- Статус архивации
SELECT * FROM pg_stat_archiver;

-- Файлы в архиве
\! ls -la /var/lib/postgresql/archive/ | head -10
```

## Решение

### Шаг 2: Результат
```
Backup completed: /var/lib/postgresql/backups/base_20250623_235500
total 8
drwxr-xr-x 2 postgres postgres 4096 Jun 23 23:55 base_20250623_235500
```

## Контрольные вопросы

1. Зачем нужен `--checkpoint=fast` в скрипте бэкапа?
2. Как `archive_timeout` влияет на потерю данных?
3. Как проверить, что бэкап полон и восстанавливаем?

## Дополнительное задание

Напишите скрипт, который проверяет последний успешный бэкап и отправляет уведомление, если бэкап не выполнялся более 24 часов.
