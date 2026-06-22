# Лабораторная работа №9: Двунаправленная логическая репликация

## Цель
Настроить двунаправленную логическую репликацию (мастер-мастер), разрешить конфликты, проверить синхронизацию.

## Теория
Двунаправленная репликация (появилась в PostgreSQL 16): оба сервера публикуют и подписываются на изменения одних и тех же таблиц. Требует осторожного проектирования для избежания конфликтов.

## Задание

### Шаг 1. Создание двух независимых серверов

```bash
# Клонируем мастер на порт 5433
pg_basebackup --pgdata=/tmp/bidir_backup --checkpoint=fast
sudo pg_ctlcluster 16 replica stop
sudo rm -rf /var/lib/postgresql/16/replica
sudo mv /tmp/bidir_backup /var/lib/postgresql/16/replica
sudo chown -R postgres:postgres /var/lib/postgresql/16/replica
sudo pg_ctlcluster 16 replica start
```

### Шаг 2. Создание таблицы на обоих серверах

```sql
-- На мастере (порт 5432)
CREATE DATABASE lab_bidir;
\c lab_bidir

CREATE TABLE orders(
    id integer PRIMARY KEY,
    source text,
    data text
);

INSERT INTO orders VALUES (1, 'master', 'initial');

-- На подписчике (порт 5433)
\! psql -p 5433 -d lab_bidir -c "
CREATE TABLE orders(
    id integer PRIMARY KEY,
    source text,
    data text
);
INSERT INTO orders VALUES (1, 'master', 'initial');
"
```

### Шаг 3. Настройка репликации

```sql
-- На мастере: публикация
CREATE PUBLICATION orders_pub FOR TABLE orders;

-- На подписчике: публикация
\! psql -p 5433 -d lab_bidir -c "CREATE PUBLICATION orders_pub FOR TABLE orders;"

-- На мастере: подписка
CREATE SUBSCRIPTION orders_sub
CONNECTION 'port=5433 user=student dbname=lab_bidir'
PUBLICATION orders_pub WITH (copy_data = false, origin = none);

-- На подписчике: подписка
\! psql -p 5433 -d lab_bidir -c "
CREATE SUBSCRIPTION orders_sub
CONNECTION 'port=5432 user=student dbname=lab_bidir'
PUBLICATION orders_pub WITH (copy_data = false, origin = none);
"
```

### Шаг 4. Тестирование

```sql
-- На мастере
INSERT INTO orders VALUES (2, 'master', 'from master');

-- На подписчике
\! psql -p 5433 -d lab_bidir -c "INSERT INTO orders VALUES (3, 'subscriber', 'from sub');"

-- На обоих серверах
SELECT * FROM orders ORDER BY id;
```

## Решение

### Шаг 4: Результат
```
-- На мастере:
 id |   source   |      data
----+------------+----------------
  1 | master     | initial
  2 | master     | from master
  3 | subscriber | from sub
(3 rows)

-- На подписчике:
 id |   source   |      data
----+------------+----------------
  1 | master     | initial
  2 | master     | from master
  3 | subscriber | from sub
(3 rows)
```

## Контрольные вопросы

1. Что такое `origin = none` и зачем он нужен?
2. Как избежать конфликтов в системе мастер-мастер?
3. Каковы ограничения двунаправленной репликации?

## Дополнительное задание

Создайте конфликт (одинаковый PK на обоих серверах) и изучите поведение системы.
