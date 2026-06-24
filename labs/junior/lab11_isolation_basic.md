# Лабораторная работа №11: Уровни изоляции

## Цель
Изучить поведение различных уровней изоляции транзакций в PostgreSQL на практике: Read Committed и Repeatable Read.

## Теория
Уровень изоляции определяет, какие изменения других транзакций видны текущей.

- **Read Committed** (по умолчанию): снимок данных создаётся в начале каждого оператора SQL. Один и тот же запрос может вернуть разные данные.
- **Repeatable Read**: снимок создаётся в начале первого оператора транзакции. Все запросы видят одну и ту же картину данных.

PostgreSQL не поддерживает Read Uncommitted (работает как Read Committed).

## Задание

### Шаг 1. Подготовка

```sql
CREATE DATABASE lab_isolation;
\c lab_isolation

CREATE TABLE items(id integer PRIMARY KEY, value text);
INSERT INTO items VALUES (1, 'original');
```

### Шаг 2. Read Committed — неповторяемое чтение

```sql
-- Сеанс 1
BEGIN;
SELECT * FROM items WHERE id = 1;
-- value = 'original'

-- Сеанс 2 (другой терминал)
BEGIN;
UPDATE items SET value = 'changed' WHERE id = 1;
COMMIT;

-- Сеанс 1
SELECT * FROM items WHERE id = 1;
-- value = 'changed' (изменилось!)
ROLLBACK;
```

### Шаг 3. Repeatable Read — повторяемое чтение

```sql
-- Восстановим данные
UPDATE items SET value = 'original' WHERE id = 1;
COMMIT;

-- Сеанс 1
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM items WHERE id = 1;
-- value = 'original'

-- Сеанс 2
BEGIN;
UPDATE items SET value = 'changed' WHERE id = 1;
COMMIT;

-- Сеанс 1
SELECT * FROM items WHERE id = 1;
-- value = 'original' (не изменилось!)
ROLLBACK;
```

### Шаг 4. Ошибка сериализации

```sql
-- Сеанс 1
BEGIN ISOLATION LEVEL REPEATABLE READ;
UPDATE items SET value = 'from_session1' WHERE id = 1;

-- Сеанс 2
BEGIN ISOLATION LEVEL REPEATABLE READ;
UPDATE items SET value = 'from_session2' WHERE id = 1;
-- Ожидание...

-- Сеанс 1
COMMIT;

-- Сеанс 2
-- ERROR: could not serialize access due to concurrent update
ROLLBACK;
```

### Шаг 5. Определение текущего уровня изоляции

```sql
SHOW default_transaction_isolation;
SELECT current_setting('default_transaction_isolation');
```

## Решение

### Шаг 2: Результат
```
-- Сеанс 1, первый SELECT:
 id |   value
----+------------
  1 | original
(1 row)

-- Сеанс 1, второй SELECT:
 id |   value
----+-----------
  1 | changed
(1 row)
```

### Шаг 3: Результат
```
-- Сеанс 1, оба SELECT:
 id |   value
----+------------
  1 | original
(1 row)
```

## Контрольные вопросы

1. Почему Read Unimplemented не поддерживается в PostgreSQL?
2. Что такое «снимок данных» и как он создаётся?
3. При каком уровне изоляции возникает ошибка сериализации?

## Дополнительное задание

Настройте уровень изоляции на DATABASE через `ALTER DATABASE` и проверьте, что он применяется при каждом новом подключении.
