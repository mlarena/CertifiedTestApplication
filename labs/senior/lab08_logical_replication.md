# Лабораторная работа №8: Логическая репликация

## Цель
Настроить логическую репликацию: создание публикаций и подписок, проверка синхронизации, мониторинг.

## Теория
Логическая репликация передаёт изменения строк (а не страниц) от публикующего сервера к подписчику. Возможна выборочная репликация отдельных таблиц. Требует `wal_level = logical`.

## Задание

### Шаг 1. Подготовка

```sql
-- На мастере
ALTER SYSTEM SET wal_level = 'logical';
```

```bash
sudo pg_ctlcluster 16 main restart
```

```sql
CREATE DATABASE lab_logrep;
\c lab_logrep

CREATE TABLE users(
    id integer PRIMARY KEY,
    name text,
    email text
);

INSERT INTO users VALUES (1, 'Alice', 'alice@test.com'), (2, 'Bob', 'bob@test.com');
```

### Шаг 2. Клонирование второго сервера

```bash
pg_basebackup --pgdata=/tmp/logrep_backup --checkpoint=fast

sudo pg_ctlcluster 16 replica stop
sudo rm -rf /var/lib/postgresql/16/replica
sudo mv /tmp/logrep_backup /var/lib/postgresql/16/replica
sudo chown -R postgres:postgres /var/lib/postgresql/16/replica
sudo pg_ctlcluster 16 replica start
```

### Шаг 3. Создание публикации

```sql
-- На мастере
CREATE PUBLICATION users_pub FOR TABLE users;
\dRp+
```

### Шаг 4. Создание подписки

```sql
-- На подписчике (порт 5433)
\! psql -p 5433 -d lab_logrep

CREATE SUBSCRIPTION users_sub
CONNECTION 'port=5432 user=student dbname=lab_logrep'
PUBLICATION users_pub;
```

### Шаг 5. Проверка репликации

```sql
-- На мастере
INSERT INTO users VALUES (3, 'Charlie', 'charlie@test.com');
UPDATE users SET email = 'alice_new@test.com' WHERE id = 1;

-- На подписчике
\! psql -p 5433 -d lab_logrep -c "SELECT * FROM users;"
```

### Шаг 6. Мониторинг

```sql
-- На подписчике
SELECT subname, pid, received_lsn, last_msg_send_time
FROM pg_stat_subscription;
```

## Решение

### Шаг 5: Результат
```
-- На подписчике:
 id |  name   |       email
----+---------+------------------
  1 | Alice   | alice_new@test.com
  2 | Bob     | bob@test.com
  3 | Charlie | charlie@test.com
(3 rows)
```

## Контрольные вопросы

1. Каковы ограничения логической репликации по сравнению с физической?
2. Что такое `replica identity` и зачем она нужна?
3. Как логическая репликация помогает при обновлении версии PostgreSQL?

## Дополнительное задание

Настройте публикацию с фильтром по столбцам и строкам.
