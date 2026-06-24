# Лабораторная работа №10: Транзакции

## Цель
Понять принципы работы транзакций в PostgreSQL: BEGIN, COMMIT, ROLLBACK, SAVEPOINT, автофиксация, ACID-свойства.

## Теория
Транзакция — последовательность операций, сохраняющих согласованность данных. PostgreSQL поддерживает четыре ACID-свойства: атомарность, согласованность, изоляция, долговечность.

По умолчанию psql работает в режиме автофиксации: каждая команда SQL выполняется в отдельной транзакции. Для группировки команд используется `BEGIN`...`COMMIT`/`ROLLBACK`.

## Задание

### Шаг 1. Транзакция с автофиксацией

```sql
CREATE DATABASE lab_transactions;
\c lab_transactions

CREATE TABLE accounts(
    id integer PRIMARY KEY,
    name text,
    balance numeric
);

INSERT INTO accounts VALUES (1, 'Алиса', 1000), (2, 'Боб', 500);
SELECT * FROM accounts;
```

### Шаг 2. Явная транзакция

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
SELECT * FROM accounts;
COMMIT;
SELECT * FROM accounts;
```

### Шаг 3. Откат транзакции

```sql
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
SELECT * FROM accounts;
ROLLBACK;
SELECT * FROM accounts;
```

### Шаг 4. Точки сохранения (SAVEPOINT)

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SAVEPOINT sp1;
UPDATE accounts SET balance = balance - 200 WHERE id = 1;
ROLLBACK TO sp1;
SELECT * FROM accounts;
-- Баланс Алисы: 900 (только первое изменение)
COMMIT;
```

### Шаг 5. Видимость изменений

```sql
-- Сеанс 1
BEGIN;
UPDATE accounts SET balance = 10000 WHERE id = 1;
-- Не коммитим!

-- Сеанс 2 (в другом терминале)
SELECT * FROM accounts WHERE id = 1;
-- Видит старое значение (900)

-- Сеанс 1
COMMIT;

-- Сеанс 2
SELECT * FROM accounts WHERE id = 1;
-- Теперь видит 10000
```

## Решение

### Шаг 2: Результат
```
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
SELECT * FROM accounts;
 id | name  | balance
----+-------+---------
  1 | Алиса |     900
  2 | Боб   |     600
(2 rows)

COMMIT;
SELECT * FROM accounts;
 id | name  | balance
----+-------+---------
  1 | Алиса |     900
  2 | Боб   |     600
(2 rows)
```

### Шаг 4: Результат
```
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SAVEPOINT sp1;
UPDATE accounts SET balance = balance - 200 WHERE id = 1;
ROLLBACK TO sp1;
SELECT * FROM accounts;
 id | name  | balance
----+-------+---------
  1 | Алиса |     800
  2 | Боб   |     600
(2 rows)
COMMIT;
```

## Контрольные вопросы

1. Что такое ACID и как каждое свойство обеспечивается в PostgreSQL?
2. Как откат к точке сохранения влияет на блокировки?
3. Почему команда DDL в PostgreSQL является транзакционной?

## Дополнительное задание

Создайте два сеанса, которые одновременно пытаются изменить одну строку. Наблюдайте за блокировкой через `pg_stat_activity`.
