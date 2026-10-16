# Лабораторная работа №8: Файлы конфигурации

## Цель
Изучить файлы конфигурации PostgreSQL: `postgresql.conf`, `postgresql.auto.conf`, механизм `ALTER SYSTEM`, представления `pg_file_settings` и `pg_settings`.

## Теория
Основной файл конфигурации — `postgresql.conf`. Он считывается при старте сервера. Дополнительные файлы подключаются директивами `include`, `include_if_exists`, `include_dir`. Файл `postgresql.auto.conf` управляется командой `ALTER SYSTEM`.

Для вступления изменений в силу необходимо перечитать конфигурацию (`pg_reload_conf()` или `SELECT pg_reload_conf()`). Некоторые параметры требуют перезапуска сервера.

## Задание

### Шаг 1. Просмотр текущей конфигурации

```sql
SHOW config_file;
SHOW data_directory;

-- Фрагмент конфигурации
SELECT pg_read_file('/etc/postgresql/16/main/postgresql.conf', 0, 200) \g (tuples_only=on format=unaligned)
```

### Шаг 2. Просмотр всех применённых настроек

```sql
SELECT sourceline, name, setting, applied, error
FROM pg_file_settings
ORDER BY sourceline;
```

### Шаг 3. Работа с pg_settings

```sql
-- Поиск параметра
SELECT name, unit, setting, boot_val, reset_val, source, context
FROM pg_settings
WHERE name = 'work_mem' \gx

-- Все параметры, требующие рестарта
SELECT name, setting, unit FROM pg_settings WHERE context = 'postmaster';
```

### Шаг 4. ALTER SYSTEM

```sql
-- Установка параметра
ALTER SYSTEM SET work_mem TO '16MB';

-- Проверка файла
SELECT pg_read_file('postgresql.auto.conf') \g (tuples_only=on format=unaligned)

-- Применение (без рестарта)
SELECT pg_reload_conf();

-- Проверка
SHOW work_mem;
```

### Шаг 5. Сброс параметра

```sql
ALTER SYSTEM RESET work_mem;
SELECT pg_reload_conf();
SHOW work_mem;
```

### Шаг 6. Создание дополнительного файла конфигурации

```bash
echo "work_mem = '8MB'" | sudo tee /etc/postgresql/16/main/conf.d/lab_workmem.conf
```

```sql
SELECT pg_reload_conf();
SHOW work_mem;
```

### Шаг 7. Горячие параметры vs требующие рестарта

```sql
-- Параметр, который можно менять на лету (session или superuser)
SELECT name, context, boot_val, reset_val
FROM pg_settings WHERE name IN ('work_mem', 'statement_timeout', 'shared_buffers');

-- shared_buffers требует рестарта — попробуем изменить на лету
ALTER SYSTEM SET shared_buffers TO '256MB';
SELECT pg_reload_conf();
SHOW shared_buffers;
-- Результат: 128MB (старое значение — не применилось!)

-- Для shared_buffers нужен restart
-- Сброс
ALTER SYSTEM RESET shared_buffers;
SELECT pg_reload_conf();

-- statement_timeout — применяется сразу
ALTER SYSTEM SET statement_timeout TO '5s';
SELECT pg_reload_conf();
SHOW statement_timeout;
-- Результат: 5s
```

### Шаг 8. Включение каталога конфига

```bash
# В postgresql.conf раскомментируйте или добавьте:
# include_dir = 'conf.d'

# Создаём файл
echo "log_min_duration_statement = 1000" \
  | sudo tee /etc/postgresql/16/main/conf.d/lab_log.conf

# Перезагрузка — параметры из conf.d загружаются автоматически
sudo -u postgres psql -c "SELECT pg_reload_conf();"
sudo -u postgres psql -c "SHOW log_min_duration_statement;"

# Удаление
sudo rm /etc/postgresql/16/main/conf.d/lab_log.conf
sudo -u postgres psql -c "SELECT pg_reload_conf();"
```

## Решение

### Шаг 4: Результат
```
SHOW work_mem;
 work_mem
----------
 16MB
(1 row)

-- После ALTER SYSTEM RESET:
 work_mem
----------
 8MB
(1 row)
```

### Шаг 6: Результат
```
SHOW work_mem;
 work_mem
----------
 8MB
(1 row)
```

## Контрольные вопросы

1. Как определить, какой файл конфигурации задаёт конкретный параметр?
2. Что будет, если один и тот же параметр указан в `postgresql.conf` и `postgresql.auto.conf`?
3. Какой контекст у параметра `work_mem` и что это значит?

## Дополнительное задание

Создайте файл конфигурации с ошибкой (например, `max_connections=5O` вместо нуля). Проверьте, что сервер не стартует, и найдите ошибку в журнале.
