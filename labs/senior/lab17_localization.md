# Лабораторная работа №17: Локализация и кодировки

## Цель
Изучить локализацию PostgreSQL: категории, провайдеры (libc/ICU), кодировки, параметры `lc_*`, обновление с удалением `lc_collate`/`lc_ctype`.

## Теория
Локализация влияет на сортировку, сравнение строк, функции upper/lower, форматирование дат/чисел.

PostgreSQL поддерживает два провайдера локалей:
- `libc` — стандартная библиотека C
- `ICU` — библиотека ICU (начиная с PostgreSQL 16)

С PostgreSQL 16 параметры `lc_collate` и `lc_ctype` удалены из серверной конфигурации — сведения о локали базы хранятся в `pg_database.datlocprovider` и `pg_database.daticulocale`.

## Задание

### Шаг 1. Текущие параметры локали

```sql
-- Все параметры lc_*
SELECT name, setting, context, short_desc
FROM pg_settings
WHERE name LIKE 'lc_%'
ORDER BY name;

-- Проверка кодировки
SHOW server_encoding;
SHOW client_encoding;
```

### Шаг 2. Информация о базе данных (PG16+)

```sql
-- Информация о локалях базы данных
SELECT datname, datlocprovider, daticulocale, datcollate, datctype
FROM pg_database
WHERE datname = current_database();

-- Провайдеры: 'c' = libc, 'i' = ICU
SELECT datname,
       CASE datlocprovider
           WHEN 'c' THEN 'libc'
           WHEN 'i' THEN 'ICU'
       END AS provider
FROM pg_database;
```

### Шаг 3. Создание базы с ICU

```sql
-- Создание базы с ICU
CREATE DATABASE lab_icu
    TEMPLATE template0
    ENCODING UTF8
    LOCALE 'C.UTF-8'
    LC_COLLATE 'C.UTF-8'
    LC_CTYPE 'C.UTF-8';

-- Проверка
\c lab_icu
SELECT datname, datlocprovider, daticulocale, datcollate, datctype
FROM pg_database WHERE datname = current_database();
```

### Шаг 4. Локализация сортировки

```sql
-- Тест сортировки
CREATE TABLE t(name text);
INSERT INTO t VALUES ('Алиса'), ('Борис'), ('Артём'), ('Виктор');

-- Сортировка по умолчанию
SELECT * FROM t ORDER BY name;

-- Сортировка по ICU
SELECT * FROM t ORDER BY name COLLATE "C";

-- Сравнение COLLATE
SELECT name,
       name = 'артём' AS equals_ci,
       name LIKE 'а%' AS starts_with_a
FROM t;
```

### Шаг 5. Параметры lc_

```sql
-- Установка lc_messages для сеанса
SET lc_messages TO 'en_US.utf8';
SELECT current_setting('lc_messages');

-- Установка lc_monetary
SET lc_monetary TO 'en_US.utf8';
SELECT to_char(1234.56, 'L999G999D99');

-- Установка lc_numeric
SET lc_numeric TO 'de_DE.utf8';
SELECT to_char(1234.56, 'FM999G999D99');

-- Установка lc_time
SET lc_time TO 'en_US.utf8';
SELECT to_char(now(), 'DD TMMonth YYYY');
```

### Шаг 6. TM-маска

```sql
-- TM-маска для дат (использует lc_time)
SET lc_time TO 'ru_RU.UTF-8';
SELECT to_char(now(), 'FMDay FMDD TMMonth YYYY');

-- Без TM — английские названия
SET lc_time TO 'en_US.utf8';
SELECT to_char(now(), 'FMDay FMDD TMMonth YYYY');
```

### Шаг 7. datestyle и форматы дат

```sql
-- Текущий datestyle
SHOW datestyle;

-- Установка формата
SET datestyle TO 'ISO, DMY';
SHOW datestyle;

-- Проверка
SELECT '01/06/2025'::date;
-- Результат зависит от datestyle!
```

### Шаг 8. Клиентская кодировка

```sql
-- Установка кодировки клиента
SET client_encoding TO 'UTF8';
SHOW client_encoding;

-- Проверка перекодирования
SET client_encoding TO 'LATIN1';
SELECT 'Привет';
-- Может вернуть ошибку или заменить символы
```

## Решение

### Шаг 2: Результат
```
 datname  | datlocprovider | daticulocale | datcollate     | datctype
----------+----------------+--------------+----------------+----------------
 lab_icu  | i              |              | C.UTF-8        | C.UTF-8
```

### Шаг 5: Результат
```
 to_char
----------
 L1.234,56
(1 row)
```

## Контрольные вопросы

1. Чем ICU отличается от libc в PostgreSQL?
2. Что произошло с `lc_collate` и `lc_ctype` в PG16?
3. Как проверить, что база создана с другой кодировкой?
4. Зачем нужен `template0` при создании базы?

## Дополнительное задание

Создайте базу с кодировкой LATIN1 и локалью ru_RU.KOI8R, проверьте сортировку и форматы дат.