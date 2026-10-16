# Лабораторная работа №3: Двухсторонняя логическая репликация

## Цель
Настроить двухстороннюю (bidirectional) репликацию с обработкой конфликтов, origin-трекингом и разрешением конфликтов.

## Теория
Двухсторонняя репликация позволяет писать на оба узла. PostgreSQL реализует её через две взаимные подписки с `origin = none`, чтобы избежать бесконечной репликации изменений.

Конфликты возникают при одновременном изменении одной строки на обоих узлах. PostgreSQL не разрешает конфликты автоматически — последнее изменение побеждает (last write wins).

## Задание

### Шаг 1. Настройка двух узлов

```bash
# Узел A (порт 5432)
sudo -u postgres psql -p 5432 -c "CREATE DATABASE bidir;"

# Узел B (порт 5433)
sudo -u postgres psql -p 5433 -c "CREATE DATABASE bidir;"
```

```sql
-- Узел A: таблица
CREATE TABLE accounts(
    id integer PRIMARY KEY,
    name text,
    balance numeric,
    updated_at timestamptz DEFAULT now()
);
INSERT INTO accounts VALUES (1, 'Алиса', 1000), (2, 'Боб', 500);
```

```sql
-- Узел B: такая же таблица
CREATE TABLE accounts(
    id integer PRIMARY KEY,
    name text,
    balance numeric,
    updated_at timestamptz DEFAULT now()
);
INSERT INTO accounts VALUES (1, 'Алиса', 1000), (2, 'Боб', 500);
```

### Шаг 2. Создание публикаций

```sql
-- Узел A
CREATE PUBLICATION pub_a FOR TABLE accounts;

-- Узел B
CREATE PUBLICATION pub_b FOR TABLE accounts;
```

### Шаг 3. Взаимные подписки

```sql
-- Узел A: подписка на B
CREATE SUBSCRIPTION sub_from_b
    CONNECTION 'host=localhost port=5433 dbname=bidir'
    PUBLICATION pub_b
    WITH (origin = none, copy_data = true);

-- Узел B: подписка на A
CREATE SUBSCRIPTION sub_from_a
    CONNECTION 'host=localhost port=5432 dbname=bidir'
    PUBLICATION pub_a
    WITH (origin = none, copy_data = true);
```

### Шаг 4. Проверка репликации

```sql
-- Узел A: изменение
UPDATE accounts SET balance = balance + 100 WHERE id = 1;

-- Узел B: проверка (через несколько секунд)
SELECT * FROM accounts WHERE id = 1;

-- Узел B: изменение
UPDATE accounts SET balance = balance + 200 WHERE id = 2;

-- Узел A: проверка
SELECT * FROM accounts WHERE id = 2;
```

### Шаг 5. Конфликт: одновременное изменение

```sql
-- Узел A и B одновременно:
-- A: UPDATE accounts SET balance = 999 WHERE id = 1;
-- B: UPDATE accounts SET balance = 888 WHERE id = 1;

-- Результат: последнее победит (last write wins)
-- На обоих узлах будет одно значение
```

### Шаг 6. Origin-трекинг

```sql
-- Проверка origin
SELECT * FROM pg_replication_origin;

-- На subscriber: проверка, какие изменения реплицированы
SELECT * FROM pg_replication_origin_status;
```

### Шаг 7. Удаление подписки и публикаций

```sql
-- Узел A
ALTER SUBSCRIPTION sub_from_b DISABLE;
DROP SUBSCRIPTION sub_from_b;
DROP PUBLICATION pub_a;

-- Узел B
ALTER SUBSCRIPTION sub_from_a DISABLE;
DROP SUBSCRIPTION sub_from_a;
DROP PUBLICATION pub_b;
```

### Шаг 8. Разрешение конфликтов

```sql
-- Скрипт разрешения конфликтов (last write wins по updated_at)
-- Запускается на каждом узле:
UPDATE accounts a
SET balance = b.balance, updated_at = b.updated_at
FROM accounts b
WHERE a.id = b.id AND b.updated_at > a.updated_at;
```

## Решение

### Шаг 4: Результат
```
 id | name  | balance | updated_at
----+-------+---------+---------------------
  1 | Алиса |    1100 | 2025-06-23 10:00:00
```

## Контрольные вопросы

1. Что делает `origin = none`?
2. Что произойдёт при бесконечной репликации без origin?
3. Как разрешаются конфликты?
4. Можно ли использовать двухстороннюю репликацию для HA?

## Дополнительное задание

Реализуйте разрешение конфликтов через триггер: если строка изменена локально позже, чем реплицирована, оставить локальное значение.