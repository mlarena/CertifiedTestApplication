# Лабораторная работа №2: Уровни изоляции — углублённо

## Цель
Детально изучить поведение Read Committed, Repeatable Read и Serializable на практике: неповторяемое чтение, фантомы, ошибки сериализации.

## Теорция
Помимо базовых различий между уровнями изоляции, важно понимать их влияние на производительность и корректность приложений. Serializable — самый строгий уровень, но вызывает ошибки сериализации, которые приложение должно обрабатывать повторными попытками.

## Задание

### Шаг 1. Неповторяемое чтение (Read Committed)

```sql
CREATE DATABASE lab_iso_adv;
\c lab_iso_adv

CREATE TABLE accounts(id integer PRIMARY KEY, balance numeric);
INSERT INTO accounts VALUES (1, 1000);

-- Сеанс 1: Read Committed (по умолчанию)
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 1000

-- Сеанс 2
UPDATE accounts SET balance = 800 WHERE id = 1;
COMMIT;

-- Сеанс 1
SELECT balance FROM accounts WHERE id = 1;  -- 800 (изменилось!)
ROLLBACK;
```

### Шаг 2. Repeatable Read — аномалия Lost Update

```sql
-- Сеанс 1
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1;  -- 800

-- Сеанс 2
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- Сеанс 1
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
-- ОШИБКА: could not serialize access due to concurrent update
ROLLBACK;
```

### Шаг 3. Serializable — полная изоляция

```sql
-- Восстановим баланс
UPDATE accounts SET balance = 1000;
COMMIT;

-- Сеанс 1
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT sum(balance) FROM accounts;  -- 1000

-- Сеанс 2
INSERT INTO accounts VALUES (2, 500);
COMMIT;

-- Сеанс 1
INSERT INTO accounts VALUES (3, 300);
COMMIT;
-- ОШИБКА: could not serialize access due to read/write dependencies
-- Означает: параллельная вставка нарушила бы результат SUM
```

### Шаг 4. Deferrable transactions

```sql
-- Для отчётов, которые не должны вызывать ошибок сериализации
BEGIN ISOLATION LEVEL SERIALIZABLE DEFERRABLE;
SELECT sum(balance) FROM accounts;
COMMIT;
```

## Решение

### Шаг 2: Результат
```
-- Сеанс 1:
UPDATE accounts SET balance = balance - 50 WHERE id = 1;
ERROR: could not serialize access due to concurrent update
CONTEXT: while locking tuple (0,1) in relation "accounts"

ROLLBACK;
```

## Контрольные вопросы

1. Что такое «Lost Update» и при каком уровне изоляции он возможен?
2. Что такое `DEFERRABLE` и когда его использовать?
3. Как приложение должно обрабатывать ошибки сериализации?

## Дополнительное задание

Измерьте производительность транзакций на разных уровнях изоляции с помощью `pgbench` с настроенным `--protocol=prepared`.
