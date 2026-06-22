# Лабораторная работа №11: Привилегии по умолчанию

## Цель
Научиться настраивать привилегии по умолчанию с помощью `ALTER DEFAULT PRIVILEGES` для автоматической выдачи/отзыва прав на новые объекты.

## Теория
По умолчанию роль `public` получает привилегии на каждую новую функцию (EXECUTE). Это удобно, но создаёт проблемы безопасности. `ALTER DEFAULT PRIVILEGES` позволяет автоматически выдавать или отзывать привилегии при создании новых объектов.

## Задание

### Шаг 1. Создание окружения

```sql
CREATE DATABASE lab_defaults;
\c lab_defaults

CREATE ROLE app_writer LOGIN PASSWORD 'writer123';
CREATE ROLE app_reader LOGIN PASSWORD 'reader123';
```

### Шаг 2. Настройка привилегий по умолчанию

```sql
-- Все новые таблицы в public: app_writer получает ALL, app_reader — SELECT
ALTER DEFAULT PRIVILEGES
    FOR ROLE app_writer
    IN SCHEMA public
    GRANT SELECT ON TABLES TO app_reader;

-- Отзыв EXECUTE у public для новых функций
ALTER DEFAULT PRIVILEGES
    FOR ROLE app_writer
    REVOKE EXECUTE ON ROUTINES FROM public;
```

### Шаг 3. Проверка

```sql
-- Под ролью app_writer
SET ROLE app_writer;

CREATE TABLE public.data_table(n integer);
INSERT INTO public.data_table VALUES (1), (2), (3);

CREATE FUNCTION public.get_count() RETURNS integer
    LANGUAGE sql STABLE RETURN (SELECT count(*) FROM public.data_table);

RESET ROLE;

-- Под ролью app_reader
SET ROLE app_reader;

SELECT * FROM public.data_table;  -- OK
SELECT public.get_count();        -- ОШИБКА: нет EXECUTE

RESET ROLE;
```

### Шаг 4. Просмотр настроек

```sql
\ddp
```

## Решение

### Шаг 4: Результат
```
              Default access privileges
  Owner  | Schema |    Type    |      Access privileges
---------+--------+------------+---------------------------
 app_writer |      | function   | app_writer=X/app_writer
 app_writer | public | table  | app_reader=r/app_writer
(2 rows)
```

## Контрольные вопросы

1. Почему `REVOKE EXECUTE ON ROUTINES FROM public` нужно делать через `ALTER DEFAULT PRIVILEGES`?
2. Как `ALTER DEFAULT PRIVILEGES` влияет на уже существующие объекты?
3. Можно ли настроить привилегии по умолчанию для всех ролей сразу?

## Дополнительное задание

Настройте так, чтобы новые таблицы в схеме `analytics` автоматически были доступны на чтение роли `analyst`.
