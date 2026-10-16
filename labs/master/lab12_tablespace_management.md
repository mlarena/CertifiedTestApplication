# Лабораторная работа №12: Управление табличными пространствами

## Цель
Изучить табличные пространства: создание, перемещение объектов, мониторинг использования, оптимизация размещения данных.

## Теория
Табличное пространство (tablespace) — это место на диске для хранения файлов таблиц, индексов и других объектов. Позволяет распределять данные по разным дискам, оптимизируя производительность и хранение.

## Задание

### Шаг 1. Создание табличных пространств

```bash
# Создание каталогов
sudo mkdir -p /mnt/fast_ssd/ts_fast
sudo mkdir -p /mnt/hdd/ts_archive
sudo chown postgres:postgres /mnt/fast_ssd/ts_fast /mnt/hdd/ts_archive
```

```sql
-- Создание табличных пространств
CREATE TABLESPACE ts_fast LOCATION '/mnt/fast_ssd/ts_fast';
CREATE TABLESPACE ts_archive LOCATION '/mnt/hdd/ts_archive';

-- Проверка
SELECT spcname, pg_tablespace_location(oid) AS location,
       pg_size_pretty(pg_tablespace_size(spcname)) AS size
FROM pg_tablespace;
```

### Шаг 2. Размещение таблиц в табличных пространствах

```sql
-- Создание таблицы в табличном пространстве
CREATE TABLE hot_data(
    id integer PRIMARY KEY,
    val text,
    created_at timestamptz DEFAULT now()
) TABLESPACE ts_fast;

INSERT INTO hot_data SELECT generate_series(1, 10000), md5(random()::text);

-- Проверка
SELECT relname, spcname
FROM pg_class c
JOIN pg_tablespace t ON t.oid = c.reltablespace
WHERE relname = 'hot_data';
```

### Шаг 3. Перемещение таблиц между табличными пространствами

```sql
-- Перемещение в табличное пространство
ALTER TABLE hot_data SET TABLESPACE ts_fast;

-- Перемещение обратно в default
ALTER TABLE hot_data SET TABLESPACE pg_default;

-- Проверка
SELECT relname,
       CASE WHEN reltablespace = 0 THEN 'pg_default'
            ELSE (SELECT spcname FROM pg_tablespace WHERE oid = reltablespace)
       END AS tablespace
FROM pg_class
WHERE relname = 'hot_data';
```

### Шаг 4. Перемещение индексов

```sql
-- Создание индекса в табличном пространстве
CREATE INDEX idx_hot_data_val ON hot_data(val) TABLESPACE ts_fast;

-- Проверка
SELECT indexname, tablename, spcname
FROM pg_indexes i
JOIN pg_class c ON c.relname = i.indexname
JOIN pg_tablespace t ON t.oid = c.reltablespace
WHERE tablename = 'hot_data';

-- Перемещение индекса
ALTER INDEX idx_hot_data_val SET TABLESPACE pg_default;
```

### Шаг 5. Установка табличного пространства по умолчанию

```sql
-- Установка по умолчанию для сеанса
SET default_tablespace = 'ts_fast';

-- Проверка
SHOW default_tablespace;

-- Создание таблицы (будет в ts_fast)
CREATE TABLE auto_ts(id integer PRIMARY KEY, val text);

-- Сброс
RESET default_tablespace;
```

### Шаг 6. Перемещение базы данных

```sql
-- Перемещение всех объектов базы в табличное пространство
ALTER DATABASE lab_db SET TABLESPACE ts_fast;

-- Проверка
SELECT datname,
       (SELECT spcname FROM pg_tablespace WHERE oid = dattablespace) AS tablespace
FROM pg_database
WHERE datname = 'lab_db';

-- Требует эксклюзивного доступа — все соединения должны быть закрыты
```

### Шаг 7. Мониторинг использования

```sql
-- Размер табличных пространств
SELECT spcname,
       pg_size_pretty(pg_tablespace_size(spcname)) AS size,
       pg_tablespace_location(spcname) AS location
FROM pg_tablespace;

-- Объекты в табличных пространствах
SELECT
    (SELECT spcname FROM pg_tablespace WHERE oid = reltablespace) AS tablespace,
    count(*) AS tables,
    pg_size_pretty(sum(pg_relation_size(oid))) AS total_size
FROM pg_class
WHERE relkind = 'r' AND reltablespace != 0
GROUP BY reltablespace;
```

### Шаг 8. Удаление табличного пространства

```sql
-- Нельзя удалить табличное пространство с объектами
DROP TABLESPACE ts_archive;
-- ERROR: tablespace "ts_archive" is not empty

-- Переместите все объекты
ALTER TABLE some_table SET TABLESPACE pg_default;

-- Теперь удаление
DROP TABLESPACE ts_archive;

-- Проверка
SELECT * FROM pg_tablespace;
```

## Решение

### Шаг 1: Результат
```
 spcname    | location              | size
------------+-----------------------+-------
 ts_fast    | /mnt/fast_ssd/ts_fast | 24 kB
 ts_archive | /mnt/hdd/ts_archive   | 24 kB
```

## Контрольные вопросы

1. Можно ли удалить табличное пространство с объектами?
2. Что произойдёт при перемещении базы данных?
3. Как default_tablespace влияет на создание таблиц?
4. Как переместить индекс между табличными пространствами?

## Дополнительное задание

Настройте автоматическое перемещение старых данных в ts_archive через событие (cron-скрипт).