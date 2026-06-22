# Лабораторная работа №9: Настройки сеанса

## Цель
Научиться управлять параметрами на уровне сеанса: SET, SHOW, RESET, set_config, пользовательские параметры.

## Теория
Многие параметры PostgreSQL можно изменять прямо во время сеанса командой `SET` или функцией `set_config`. Значение действует до конца сеанса (по умолчанию) или до конца транзакции (`SET LOCAL`). При откате транзакции изменения параметров также откатываются.

Пользовательские параметры (имя содержит точку) могут использоваться как глобальные переменные сеанса.

## Задание

### Шаг 1. Базовые операции

```sql
-- Получение текущего значения
SHOW work_mem;

-- Установка для сеанса
SET work_mem TO '24MB';
SHOW work_mem;

-- Чтение через функцию
SELECT current_setting('work_mem');

-- Сброс к начальному значению
RESET work_mem;
SHOW work_mem;
```

### Шаг 2. SET LOCAL

```sql
BEGIN;
SET LOCAL work_mem TO '64MB';
SHOW work_mem;
-- work_mem = 64MB

COMMIT;
SHOW work_mem;
-- work_mem = значение до транзакции
```

### Шаг 3. Откат транзакции

```sql
BEGIN;
SET work_mem TO '32MB';
SHOW work_mem;
-- work_mem = 32MB

ROLLBACK;
SHOW work_mem;
-- work_mem = значение до BEGIN
```

### Шаг 4. Функция set_config

```sql
SELECT set_config('work_mem', '48MB', false);  -- до конца сеанса
SHOW work_mem;

SELECT set_config('work_mem', '64MB', true);   -- до конца транзакции
SHOW work_mem;
```

### Шаг 5. Пользовательские параметры

```sql
-- Создание пользовательского параметра
SELECT set_config('myapp.currency', 'RUB', false);

-- Чтение
SELECT current_setting('myapp.currency');

-- Проверка существования
SELECT current_setting('myapp.currency', true);

-- Через SET
SET myapp.region = 'EU';
SHOW myapp.region;
```

### Шаг 6. Все установленные переменные

```sql
\set
```

## Решение

### Шаг 1: Результат
```
SHOW work_mem;
 work_mem
----------
 4MB
(1 row)

SET work_mem TO '24MB';
SHOW work_mem;
 work_mem
----------
 24MB
(1 row)

RESET work_mem;
SHOW work_mem;
 work_mem
----------
 4MB
(1 row)
```

### Шаг 2: Результат
```
BEGIN;
SET LOCAL work_mem TO '64MB';
SHOW work_mem;
 work_mem
----------
 64MB
(1 row)

COMMIT;
SHOW work_mem;
 work_mem
----------
 4MB
(1 row)
```

## Контрольные вопросы

1. Чем `SET` отличается от `SET LOCAL`?
2. Что произойдёт с параметром, установленным через `SET`, при `ROLLBACK`?
3. Зачем нужны пользовательские параметры и какое ограничение на их имена?

## Дополнительное задание

Напишите psql-скрипт, который проверяет, установлен ли параметр `myapp.tenant_id`, и если нет — устанавливает значение по умолчанию.
