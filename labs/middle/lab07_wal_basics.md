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
