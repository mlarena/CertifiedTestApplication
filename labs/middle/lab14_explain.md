# Лабораторная работа №14: EXPLAIN ANALYZE

## Цель
Научиться читать планы выполнения запросов, понимать Seq Scan vs Index Scan, Cost и Actual time, влияние индексов.

## Теория
`EXPLAIN ANALYZE` выполняет запрос и показывает реальный план выполнения с фактическими метриками. Основные операторы: Seq Scan (последовательное сканирование), Index Scan (индексный доступ), Hash Join, Merge Join, Sort.

## Задание

### Шаг 1. Подготовка

```sql
CREATE DATABASE lab_explain;
\c lab_explain

CREATE TABLE orders(
    id integer PRIMARY KEY,
    customer_id integer,
    amount numeric,
    created_at timestamptz DEFAULT now()
);

INSERT INTO orders
SELECT id, (random() * 1000)::integer, (random() * 10000)::numeric,
       now() - (random() * 365)::integer * interval '1 day'
FROM generate_series(1, 1000000) AS id;

CREATE INDEX idx_orders_customer ON orders(customer_id);
ANALYZE orders;
```

### Шаг 2. Seq Scan vs Index Scan

```sql
-- Seq Scan (без условия по индексу)
EXPLAIN (analyze, costs off)
SELECT * FROM orders WHERE customer_id = 42;

-- Добавим индекс и сравним
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
EXPLAIN (analyze, costs off)
SELECT * FROM orders WHERE customer_id = 42;
```

### Шаг 3. Анализ стоимости

```sql
-- Смотрим cost (до выполнения)
EXPLAIN (costs on)
SELECT * FROM orders WHERE customer_id = 42;

-- Смотрим actual (после выполнения)
EXPLAIN (analyze, timing on)
SELECT * FROM orders WHERE customer_id = 42;
```

### Шаг 4. Хеш-соединение

```sql
CREATE TABLE customers(
    id integer PRIMARY KEY,
    name text
);

INSERT INTO customers SELECT id, md5(id::text) FROM generate_series(1, 1000) AS id;
ANALYZE customers;

EXPLAIN (analyze, costs off)
SELECT c.name, count(*)
FROM orders o JOIN customers c ON o.customer_id = c.id
GROUP BY c.name;
```

### Шаг 5. Сортировка

```sql
EXPLAIN (analyze, costs off)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 100;

-- С индексом
CREATE INDEX idx_orders_created ON orders(created_at);
EXPLAIN (analyze, costs off)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 100;
```

## Решение

### Шаг 2: Результат
```
-- Без индекса:
Seq Scan on orders  (actual rows=10 loops=1)
  Filter: (customer_id = 42)
  Rows Removed by Filter: 999990
  Buffers: shared hit=4432
Execution Time: 45.678 ms

-- С индексом:
Index Scan using idx_orders_customer on orders  (actual rows=10 loops=1)
  Index Cond: (customer_id = 42)
  Buffers: shared hit=15
Execution Time: 0.123 ms
```

## Контрольные вопросы

1. Что означает `Rows Removed by Filter`?
2. Когда Seq Scan быстрее Index Scan?
3. Как использовать `EXPLAIN (ANALYZE, BUFFERS)` для анализа I/O?

## Дополнительное задание

Сравните планы для запроса `SELECT count(*) FROM orders WHERE customer_id BETWEEN 100 AND 200` с индексом и без.
