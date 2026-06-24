# Лабораторная работа №2: Логическое восстановление (pg_restore)

## Цель
Освоить утилиту pg_restore: восстановление из форматов custom и directory, фильтрация объектов, параллельный режим.

## Теория
`pg_restore` читает файлы в форматах custom, directory или tar и восстанавливает объекты. Преимущества: можно выбрать объекты для восстановления, параллельное выполнение, восстановление без пересоздания БД.

## Задание

### Шаг 1. Подготовка резервных копий

```sql
-- Создадим две копии для экспериментов
CREATE DATABASE lab_restore1;
CREATE DATABASE lab_restore2;
CREATE DATABASE lab_restore3;
```

```bash
# Копия в формате custom
pg_dump -d lab_backup -Fc -f /tmp/full.dump

# Копия в формате directory
mkdir -p /tmp/full_dir
pg_dump -d lab_backup -Fd -j 2 -f /tmp/full_dir
```

### Шаг 2. Просмотр содержимого копии

```bash
pg_restore --list /tmp/full.dump | head -30
```

### Шаг 3. Полное восстановление

```bash
pg_restore -d lab_restore1 /tmp/full.dump
```

```sql
\c lab_restore1
SELECT count(*) FROM products;
```

### Шаг 4. Восстановление только определённых объектов

```bash
# Только таблица products (без индексов)
pg_restore -d lab_restore2 -t products --no-indexes /tmp/full.dump
```

```sql
\c lab_restore2
\d products  -- Таблица есть
\di          -- Индексов нет
```

### Шаг 5. Параллельное восстановление

```bash
pg_restore -d lab_restore3 -j 4 /tmp/full_dir
```

### Шаг 6. Восстановление с пересозданием

```sql
DROP DATABASE lab_restore1;
CREATE DATABASE lab_restore1 TEMPLATE template0 ENCODING = 'UTF8';
```

```bash
pg_restore -d lab_restore1 --create --clean /tmp/full.dump
```

## Решение

### Шаг 2: Результат
```
; Archive created at 2025-06-23 23:50:00+03
;     on database: lab_backup
;     by pg_dump version: 16.9
;
; TOC Section:
;
;  - 2 - 12345 TABLE public products postgres
;  - 3 - 12346 TABLE DATA public products postgres
;  - 4 - 12347 INDEX public idx_prod_name postgres
```

## Контрольные вопросы

1. Чем `pg_restore --create` отличается от `--create --clean`?
2. Как восстановить только данные без схемы?
3. Что такое `--if-exists` и когда он полезен?

## Дополнительное задание

Восстановите конкретную таблицу с новым именем (используя `--schema` и редактирование скрипта).
