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

### Шаг 7. Защита от долгих запросов и блокировок

```sql
-- Таймаут выполнения запроса (защита от зависших SELECT)
SET statement_timeout TO '5s';
SHOW statement_timeout;

-- Таймаут ожидания блокировки (защита от взаимных блокировок)
SET lock_timeout TO '3s';
SHOW lock_timeout;

-- Таймаут простоя в транзакции (защита от idle in transaction)
SET idle_in_transaction_session_timeout TO '30s';
SHOW idle_in_transaction_session_timeout;

-- Сброс
RESET statement_timeout;
RESET lock_timeout;
RESET idle_in_transaction_session_timeout;
```

### Шаг 8. Temp buffers

```sql
-- Размер буферов для временных таблиц
SHOW temp_buffers;

-- Установка большего размера для сеанса
SET temp_buffers TO '16MB';
SHOW temp_buffers;

-- Создание и использование временной таблицы
CREATE TEMP TABLE tmp_lab(n integer);
INSERT INTO tmp_lab SELECT generate_series(1, 1000);
SELECT count(*) FROM tmp_lab;

-- Сброс
RESET temp_buffers;
```

### Шаг 9. Параметры на уровне роли

```sql
-- Установка параметра для роли (применяется при входе в сеанс)
CREATE ROLE lab_role LOGIN;
ALTER ROLE lab_role SET work_mem TO '32MB';
ALTER ROLE lab_role SET statement_timeout TO '10s';

-- Проверка
SELECT rolname, rolconfig FROM pg_roles WHERE rolname = 'lab_role';

-- Очистка
ALTER ROLE lab_role RESET ALL;
DROP ROLE lab_role;
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
