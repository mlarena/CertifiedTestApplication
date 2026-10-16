# Лабораторная работа №7: WAL — основы

## Цель
Изучить журнал упреждающей записи (WAL): уровни журнала, LSN, сегменты, влияние на надёжность и производительность.

## Теория
WAL (Write-Ahead Log) — механизм журналирования, обеспечивающий долговечность транзакций. Записи WAL попадают на диск раньше, чем изменённые страницы данных. Уровни журнала: `minimal`, `replica` (по умолчанию), `logical`.

## Задание

### Шаг 1. Текущая позиция WAL

```sql
SELECT pg_current_wal_lsn();
```

### Шаг 2. Наблюдение за ростом WAL

```sql
CREATE DATABASE lab_wal;
\c lab_wal

-- Запоминаем позицию
SELECT pg_current_wal_lsn() AS start_lsn \gset

-- Выполняем операции
CREATE TABLE t(n integer);
INSERT INTO t SELECT id FROM generate_series(1, 10000);

-- Сравниваем
SELECT pg_current_wal_lsn()::text - :start_lsn::text AS wal_bytes;
```

### Шаг 3. Уровни журнала

```sql
SHOW wal_level;

-- Все уровни
SELECT name, setting, short_desc
FROM pg_settings WHERE name = 'wal_level';
```

### Шаг 4. Файлы WAL

```sql
-- Список файлов WAL
SELECT name, size, modification
FROM pg_ls_waldir()
ORDER BY name;
```

### Шаг 5. Контрольная точка

```sql
-- Выполнение контрольной точки
CHECKPOINT;

-- Проверка журнала
\! tail -n 10 /var/log/postgresql/postgresql-16-main.log | grep -i checkpoint
```

### Шаг 6. Анализ WAL-активности

```sql
-- Размер WAL
SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS total_wal_bytes;

-- Количество сегментов
SELECT count(*) FROM pg_ls_waldir();
```

### Шаг 7. Использование pg_waldump

```bash
# Установка
sudo apt-get install -y postgresql-16-wal-tools

# Чтение WAL-сегмента
sudo -u postgres pg_waldump /var/lib/postgresql/16/main/pg_wal/000000010000000000000001 -n 5

# Фильтрация по типу записи
sudo -u postgres pg_waldump /var/lib/postgresql/16/main/pg_wal/000000010000000000000001 \
  --rmgr Heap --limit 3

# Анализ контрольной точки
sudo -u postgres pg_waldump /var/lib/postgresql/16/main/pg_wal/000000010000000000000001 \
  --rmgr Checkpoint --limit 1
```

### Шаг 8. Использование pg_walinspect

```sql
CREATE EXTENSION pg_walinspect;

-- Все записи WAL
SELECT pg_lsn, pg_wal_lsn_diff(first_lsn, 0) AS offset,
       rmgr, action, description
FROM pg_wal_decode_record(
    pg_wal_lsn_bound(1024),
    pg_wal_lsn_bound(2048)
)
LIMIT 10;

-- Текущая позиция вставки
SELECT pg_current_wal_insert_lsn();

-- Разница WAL между двумя LSN
SELECT pg_wal_lsn_diff(
    '0/1FF1260'::pg_lsn,
    '0/1F00000'::pg_lsn
) AS bytes_between;

-- Имя файла WAL для LSN
SELECT pg_walfile_name('0/1FF1260');

-- Список всех сегментов WAL
SELECT * FROM pg_ls_waldir();
```

### Шаг 9. Мониторинг WAL-активности

```sql
-- Количество записей WAL на операцию
SELECT name, setting
FROM pg_stat_database
WHERE datname = current_database()
AND name LIKE '%wal%';

-- Размер WAL-каталога
SELECT pg_size_pretty(pg_database_size('postgres')) AS db_size;
-- Или:
SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0'));
```

### Шаг 10. Настройка уровня журнала

```sql
-- Текущий уровень
SHOW wal_level;
-- replica (по умолчанию)

-- Возможные значения: minimal, replica, logical
-- Для логической репликации:
-- ALTER SYSTEM SET wal_level = 'logical';
-- SELECT pg_reload_conf();
-- (требуется рестарт сервера!)

-- Мониторинг WAL-производительности
SELECT * FROM pg_stat_wal;
```

## Решение

### Шаг 2: Результат
```
   start_lsn
----------------
 0/1922118
(1 row)

 wal_bytes
----------
    12312
(1 row)
```

## Контрольные вопросы

1. Что такое LSN и как он используется?
2. Почему WAL должен попасть на диск раньше данных?
3. Чем файловый архив WAL отличается от потокового?

## Дополнительное задание

Настройте файловый архив WAL с помощью `archive_command` и проверьте, что сегменты копируются в архивный каталог.
