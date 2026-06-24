# Лабораторная работа №7: Табличные пространства

## Цель
Понять назначение табличных пространств, научиться создавать их и назначать базам данных и таблицам.

## Теория
Табличное пространство (tablespace) определяет расположение данных в файловой системе. При инициализации кластера создаются два табличных пространства: `pg_default` (по умолчанию) и `pg_global` (общие объекты кластера).

Табличные пространства позволяют распределять данные по разным дискам (быстрые SSD для горячих данных, медленные HDD для архивных).

## Задание

### Шаг 1. Создание каталога для табличного пространства

```bash
sudo -u postgres mkdir /var/lib/postgresql/ts_lab
```

### Шаг 2. Создание табличного пространства

```sql
CREATE TABLESPACE lab_ts LOCATION '/var/lib/postgresql/ts_lab';
\db+
```

### Шаг 3. Назначение БД по умолчанию

```sql
CREATE DATABASE lab tablespaces;
\c lab tablespaces

-- Создадим таблицу — она попадёт в lab_ts
CREATE TABLE t1(n integer);
\d t1
```

### Шаг 4. Явное указание табличного пространства

```sql
CREATE TABLE t2(n integer) TABLESPACE pg_default;
\d t2

-- Индекс в другом ТП
CREATE INDEX t2_idx ON t2(n) TABLESPACE lab_ts;
\d t2
```

### Шаг 5. Просмотр файловой системы

```sql
-- Путь к файлу таблицы
SELECT pg_relation_filepath('t1');

-- Путь через OID
SELECT oid FROM pg_tablespace WHERE spcname = 'lab_ts';
\! ls -l /var/lib/postgresql/16/main/pg_tblspc/
```

### Шаг 6. Перемещение объектов

```sql
ALTER TABLE t1 SET TABLESPACE pg_default;
SELECT tablename, tablespace FROM pg_tables WHERE schemaname = 'public';
```

### Шаг 7. Размер табличного пространства

```sql
SELECT pg_size_pretty(pg_tablespace_size('lab_ts'));
\db+
```

### Шаг 8. Удаление

```sql
-- Удаляем таблицы и индексы из ТП
DROP TABLE t1;
DROP TABLE t2;

-- Смена ТП по умолчанию для БД
\c postgres
ALTER DATABASE lab tablespaces SET TABLESPACE pg_default;

-- Удаление ТП
DROP TABLESPACE lab_ts;

-- Удаление каталога
\! sudo -u postgres rm -rf /var/lib/postgresql/ts_lab
```

## Решение

### Шаг 3: Результат
```
\d t1
Table "public.t1"
 Column |  Type   | Collation | Nullable | Default
--------+---------+-----------+----------+---------
 n      | integer |           |          |
Tablespace: "lab_ts"
```

## Контрольные вопросы

1. Почему `ALTER TABLE ... SET TABLESPACE` — это физическая операция?
2. Можно ли удалить табличное пространство, содержащее объекты?
3. Как связать `random_page_cost` с табличным пространством на SSD?

## Дополнительное задание

Создайте два табличных пространства (одно на «быстрых» дисках, другое на «медленных») и настройте `random_page_cost` для каждого. Распределите таблицы по ним в зависимости от частоты обращений.
