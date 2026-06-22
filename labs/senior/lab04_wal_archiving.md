# Лабораторная работа №4: Непрерывное архивирование WAL

## Цель
Настроить непрерывное архивирование журналов предзаписи: файловый архив (archive_command) и потоковый архив (pg_receivewal).

## Теория
Непрерывное архивирование позволяет восстановить кластер на произвольный момент времени. Файловый архив: процесс archiver копирует заполненные сегменты WAL. Потоковый архив: утилита pg_receivewal получает записи по протоколу репликации.

## Задание

### Шаг 1. Создание каталога для архива

```bash
sudo -u postgres mkdir /var/lib/postgresql/archive
sudo -u postgres chmod 700 /var/lib/postgresql/archive
```

### Шаг 2. Настройка параметров

```sql
-- Включаем архивирование
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'test ! -f /var/lib/postgresql/archive/%f && cp %p /var/lib/postgresql/archive/%f';
ALTER SYSTEM SET wal_level = 'replica';
```

```bash
sudo pg_ctlcluster 16 main restart
```

### Шаг 3. Проверка работы архива

```sql
-- Выполняем операции для генерации WAL
CREATE DATABASE lab_archive;
\c lab_archive
CREATE TABLE t AS SELECT * FROM generate_series(1, 100000);

-- Выполняем контрольную точку для переключения сегмента
CHECKPOINT;
```

```bash
# Проверяем архив
sudo -u postgres ls -la /var/lib/postgresql/archive/
```

### Шаг 4. Потоковый архив (pg_receivewal)

```bash
# Создаём слот
sudo -u postgres pg_receivewal --create-slot --slot=archive_slot

# Запускаем в фоне
sudo -u postgres pg_receivewal -D /var/lib/postgresql/archive --slot=archive_slot &
```

```sql
-- Генерируем нагрузку
UPDATE t SET id = id + 1;
CHECKPOINT;
```

```bash
# Проверяем архив
sudo -u postgres ls -la /var/lib/postgresql/archive/
```

### Шаг 5. Архивные параметры

```sql
SELECT name, setting
FROM pg_settings
WHERE name IN ('archive_mode', 'archive_command', 'archive_timeout', 'wal_level');
```

## Решение

### Шаг 3: Результат
```
sudo -u postgres ls -la /var/lib/postgresql/archive/
-rw------- 1 postgres postgres 16777216 Jun 23 23:55 000000010000000000000001
```

## Контрольные вопросы

1. Что будет, если archive_command завершится с ошибкой?
2. Как `archive_timeout` влияет на архивирование?
3. Зачем нужен слот репликации для pg_receivewal?

## Дополнительное задание

Настройте архивирование на удалённый сервер с помощью `rsync` в archive_command.
