# Лабораторная работа №14: Параллельное резервное копирование и восстановление

## Цель
Освоить параллельное резервное копирование и восстановление: pg_dump --jobs, pg_restore --jobs, pg_dumpall --globals-only, оптимизация времени бэкапа.

## Теория
Параллельное резервное копирование позволяет значительно сократить время создания и восстановления бэкапов для больших баз данных.

Форматы:
- `plain` — SQL-скрипт (не поддерживает параллельное восстановление)
- `custom` — сжатый архив с оглавлением
- `directory` — директория с файлами (поддерживает параллельное восстановление)

## Задание

### Шаг 1. Создание тестовой базы

```sql
CREATE DATABASE lab_parallel;
\c lab_parallel

-- Создание таблиц
CREATE TABLE t1(id integer PRIMARY KEY, val text);
CREATE TABLE t2(id integer PRIMARY KEY, val text);
CREATE TABLE t3(id integer PRIMARY KEY, val text);

-- Вставка данных
INSERT INTO t1 SELECT generate_series(1, 1000000), md5(random()::text);
INSERT INTO t2 SELECT generate_series(1, 1000000), md5(random()::text);
INSERT INTO t3 SELECT generate_series(1, 1000000), md5(random()::text);

-- Индексы
CREATE INDEX idx_t1_val ON t1(val);
CREATE INDEX idx_t2_val ON t2(val);
CREATE INDEX idx_t3_val ON t3(val);
```

### Шаг 2. Последовательное резервное копирование

```bash
# Последовательный бэкап (1 поток)
time pg_dump -d lab_parallel -Fc -f /tmp/sequential_backup.dump

# Проверка размера
ls -lh /tmp/sequential_backup.dump
```

### Шаг 3. Параллельное резервное копирование

```bash
# Параллельный бэкап (4 потока, directory формат)
mkdir -p /tmp/parallel_backup_dir
time pg_dump -d lab_parallel -Fd -j 4 -f /tmp/parallel_backup_dir

# Проверка
ls -lh /tmp/parallel_backup_dir/
```

### Шаг 4. Экспорт глобальных объектов

```bash
# pg_dumpall — глобальные объекты (роли, tablespaces)
pg_dumpall --globals-only -f /tmp/globals.sql

# Проверка
head -20 /tmp/globals.sql
grep -i 'role\|tablespace' /tmp/globals.sql
```

### Шаг 5. Последовательное восстановление

```bash
# Создание базы
psql -c "CREATE DATABASE lab_restore;"

# Последовательное восстановление
time pg_restore -d lab_restore --no-owner --no-privileges /tmp/sequential_backup.dump
```

### Шаг 6. Параллельное восстановление

```bash
# Создание базы
psql -c "CREATE DATABASE lab_restore_parallel;"

# Параллельное восстановление (4 потока)
time pg_restore -d lab_restore_parallel -j 4 --no-owner --no-privileges \
  /tmp/parallel_backup_dir/

# Проверка
psql -d lab_restore_parallel -c "SELECT count(*) FROM t1;"
```

### Шаг 7. Оптимизация времени восстановления

```bash
# Увеличение work_mem для восстановления
export PGOPTIONS='-c work_mem=256MB'
pg_restore -d lab_restore_parallel -j 4 --no-owner --no-privileges \
  /tmp/parallel_backup_dir/

# Отключение autovacuum на время восстановления
export PGOPTIONS='-c autovacuum=off -c fsync=off'
pg_restore -d lab_restore_parallel -j 4 --no-owner --no-privileges \
  /tmp/parallel_backup_dir/
```

### Шаг 8. Полное восстановление с globals

```bash
# Полное восстановление: globals + database
psql -f /tmp/globals.sql
pg_restore -d lab_parallel -j 4 --no-owner --no-privileges \
  /tmp/parallel_backup_dir/
```

### Шаг 9. Мониторинг восстановления

```bash
# pg_stat_activity во время восстановления
psql -c "SELECT pid, state, query FROM pg_stat_activity WHERE query LIKE '%CREATE%';"

# Проверка прогресса
psql -d lab_restore_parallel -c "SELECT relname, pg_size_pretty(pg_relation_size(oid)) FROM pg_stat_user_tables;"
```

## Решение

### Шаг 2: Результат
```
real    2m15s
user    0m45s
sys     0m12s
```

### Шаг 3: Результат
```
real    0m38s
user    1m12s
sys     0m8s
```

## Контрольные вопросы

1. Почему directory формат быстрее для восстановления?
2. Что делает pg_dumpall --globals-only?
3. Можно ли использовать -j с plain-форматом?
4. Как оптимизировать время восстановления?

## Дополнительное задание

Напишите скрипт автоматического резервного копирования с параллельным режимом, сжатием и ротацией архивов.