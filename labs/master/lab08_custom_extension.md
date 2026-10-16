# Лабораторная работа №8: Создание пользовательского расширения

## Цель
Создать собственное расширение с SQL-скриптами, компилируемым кодом (PGXS), управлением версиями и обновлением.

## Теория
Расширение PostgreSQL состоит из:
- `.control` файла (метаданные)
- SQL-скриптов создания/обновления
- Компилируемого кода (C-код, сборка через PGXS)

PGXS (PostgreSQL Extension Build System) — система сборки для расширений.

## Задание

### Шаг 1. Подготовка PGXS

```bash
# Установка пакетов для разработчика
sudo apt-get install -y postgresql-server-dev-16

# Проверка pg_config
pg_config --version
pg_config --bindir
pg_config --pgxs
```

### Шаг 2. Создание структуры расширения

```bash
mkdir -p /tmp/my_extension/sql
cd /tmp/my_extension

# Создание control-файла
cat > my_extension.control << EOF
comment = 'My custom extension'
default_version = '1.0'
relocatable = true
schema = my_schema
EOF

# Создание SQL-скрипта создания
cat > sql/my_extension--1.0.sql << EOF
-- CREATE EXTENSION my_extension

CREATE OR REPLACE FUNCTION my_extension_version()
RETURNS text AS $$
    SELECT '1.0';
$$ LANGUAGE SQL IMMUTABLE;

CREATE TABLE my_extension_config(
    key text PRIMARY KEY,
    value text,
    updated_at timestamptz DEFAULT now()
);

CREATE VIEW my_extension_status AS
SELECT
    count(*) FILTER (WHERE value IS NOT NULL) AS active_configs,
    count(*) FILTER (WHERE value IS NULL) AS null_configs
FROM my_extension_config;
EOF

# Создание SQL-скрипта удаления
cat > sql/my_extension--1.0--1.1.sql << EOF
-- Version update 1.0 -> 1.1

ALTER FUNCTION my_extension_version() RETURNS text AS $$
    SELECT '1.1';
$$ LANGUAGE SQL IMMUTABLE;

ALTER TABLE my_extension_config ADD COLUMN description text;
EOF

# Создание SQL-скрипта обновления
cat > sql/my_extension--1.1.sql << EOF
-- Do nothing for 1.1 -> 1.1
EOF
```

### Шаг 3. Создание Makefile

```bash
# PGXS-based Makefile
cat > Makefile << EOF
MODULES = my_extension
EXTENSION = my_extension
DATA = my_extension--1.0.sql my_extension--1.0--1.1.sql my_extension--1.1.sql

PG_CONFIG = pg_config
PGXS := \$(pg_config --pgxs)
include \$(PGXS)
EOF
```

### Шаг 4. Сборка и установка

```bash
# Сборка
make

# Установка
sudo make install

# Проверка
ls /usr/share/postgresql/16/extension/my_extension*
ls /usr/share/postgresql/16/extension/my_extension--*
```

### Шаг 5. Установка расширения

```sql
-- Установка
CREATE EXTENSION my_extension;

-- Проверка
SELECT * FROM pg_extension WHERE extname = 'my_extension';

-- Тест функции
SELECT my_extension_version();

-- Работа с таблицей
INSERT INTO my_extension_config(key, value) VALUES ('setting1', 'value1');

-- Тест представления
SELECT * FROM my_extension_status;
```

### Шаг 6. Обновление расширения

```sql
-- Обновление до 1.1
ALTER EXTENSION my_extension UPDATE;

-- Проверка
SELECT my_extension_version();
-- Результат: 1.1

-- Проверка новой колонки
\d my_extension_config
```

### Шаг 7. Перемещение схемы

```sql
-- Создание новой схемы
CREATE SCHEMA my_ext_schema;

-- Перемещение расширения
ALTER EXTENSION my_extension SET SCHEMA my_ext_schema;

-- Проверка
SELECT n.nspname, e.extname
FROM pg_extension e
JOIN pg_namespace n ON n.oid = e.extschema;
```

### Шаг 8. Удаление расширения

```sql
-- Удаление
DROP EXTENSION my_extension;

-- Проверка
SELECT * FROM pg_extension WHERE extname = 'my_extension';
```

## Решение

### Шаг 5: Результат
```
 my_extension_version 
----------------------
 1.0
(1 row)
```

### Шаг 6: Результат
```
 my_extension_version 
----------------------
 1.1
(1 row)
```

## Контрольные вопросы

1. Зачем нужен control-файл?
2. Как работают скрипты обновления версий?
3. Что делает PGXS?
4. Можно ли переместить расширение в другую схему?

## Дополнительное задание

Создайте расширение с C-кодом, которое реализует функцию для хеширования строк.