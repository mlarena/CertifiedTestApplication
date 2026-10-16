# Лабораторная работа №16: Расширения PostgreSQL

## Цель
Изучить механизм расширений: создание, установка, обновление версий, PGXS, работа с pg_dump.

## Теория
Расширение (extension) — это набор связанных объектов БД, управляемых как единое целое. PostgreSQL поддерживает автоматическое управление версиями, обновления и корректную работу с `pg_dump`.

Расширение состоит из:
- Управляющего файла `.control` (описание)
- SQL-скриптов создания/обновления `имя--версия.sql`
- Компилируемого кода (опционально)

## Задание

### Шаг 1. Доступные и установленные расширения

```sql
-- Все доступные расширения
SELECT * FROM pg_available_extensions
ORDER BY name;

-- Установленные расширения
SELECT * FROM pg_extension;

-- Информация об установленном расширении
SELECT e.extname, e.extversion, e.extschema, e.extowner::regrole
FROM pg_extension e;
```

### Шаг 2. Установка и использование расширений

```sql
-- pg_stat_statements — статистика запросов
CREATE EXTENSION pg_stat_statements;

-- Проверка
SELECT count(*) FROM pg_stat_statements;

-- pageinspect — анализ страниц
CREATE EXTENSION pageinspect;

-- Проверка
SELECT * FROM heap_page_items(get_page('pg_class', 0)) LIMIT 3;
```

### Шаг 3. ALTER EXTENSION — изменение схемы

```sql
-- Перемещение в другую схему
CREATE SCHEMA my_ext;

ALTER EXTENSION pg_stat_statements SET SCHEMA my_ext;

-- Проверка
SELECT n.nspname, e.extname
FROM pg_extension e
JOIN pg_namespace n ON n.oid = e.extschema;
```

### Шаг 4. Обновление версий

```sql
-- Текущая версия
SELECT extname, extversion FROM pg_extension WHERE extname = 'pageinspect';

-- Обновление до последней версии
ALTER EXTENSION pageinspect UPDATE;

-- Проверка
SELECT extname, extversion FROM pg_extension WHERE extname = 'pageinspect';
```

### Шаг 5. pg_dump и расширения

```sql
-- Создание таблицы и расширение
CREATE TABLE t(id integer PRIMARY KEY);
CREATE EXTENSION pageinspect;

-- Экспорт
pg_dump -d lab_extensions --schema-only > /tmp/schema.sql
pg_dump -d lab_extensions --data-only > /tmp/data.sql

-- Проверка содержимого
grep -i 'extension' /tmp/schema.sql
```

### Шаг 6. Зависимости между объектами

```sql
-- Создание таблицы и функции из расширения
CREATE TABLE test_table(id integer PRIMARY KEY);

CREATE FUNCTION test_func() RETURNS integer AS $$
    SELECT 1;
$$ LANGUAGE SQL;

-- Проверка зависимостей
SELECT
    p.proname,
    pg_get_function_identity_arguments(p.oid) AS args,
    pg_get_functiondef(p.oid) AS definition
FROM pg_proc p
JOIN pg_extension e ON e.oid = p.pronamespace
JOIN pg_namespace n ON n.oid = e.extschema;
```

### Шаг 7. pg_dumpall и расширения

```bash
# pg_dumpall — экспорт глобальных объектов
pg_dumpall --globals-only > /tmp/globals.sql

# Проверка
grep -i 'extension' /tmp/globals.sql

# pg_dump — экспорт с информацией о расширениях
pg_dump -d lab_extensions > /tmp/full_dump.sql
grep -A5 'pg_stat_statements' /tmp/full_dump.sql
```

### Шаг 8. Удаление расширений

```sql
-- Удаление расширения
DROP EXTENSION pg_stat_statements;

-- Проверка
SELECT * FROM pg_extension;

-- Восстановление
CREATE EXTENSION pg_stat_statements;
```

## Решение

### Шаг 3: Результат
```
 ALTER EXTENSION
```

### Шаг 4: Результат
```
 extname    | extversion
------------+------------
 pageinspect| 1.16
```

## Контрольные вопросы

1. Чем расширение отличается от обычной схемы?
2. Что произойдёт при удалении таблицы из расширения?
3. Как pg_dump определяет, какие объекты принадлежат расширению?
4. Можно ли установить расширение в другую схему?

## Дополнительное задание

Создайте собственное простое расширение с SQL-скриптами создания/удаления и установите его.