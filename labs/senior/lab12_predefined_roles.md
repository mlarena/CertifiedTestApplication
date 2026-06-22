# Лабораторная работа №12: Предопределённые роли

## Цель
Изучить предопределённые роли PostgreSQL: pg_read_all_data, pg_write_all_data, pg_monitor и др., настроить доступ без суперпользовательских полномочий.

## Теория
PostgreSQL предоставляет набор предопределённых ролей для типичных административных задач. Использование этих ролей позволяет делегировать права без предоставления суперпользовательского доступа.

## Задание

### Шаг 1. Просмотр предопределённых ролей

```sql
\duS
```

### Шаг 2. Создание роли мониторинга

```sql
CREATE ROLE monitoring LOGIN PASSWORD 'monitor123';

-- Предоставляем доступ к статистике
GRANT pg_read_all_stats TO monitoring;
GRANT pg_stat_scan_tables TO monitoring;
```

### Шаг 3. Проверка доступа

```bash
psql -U monitoring -d postgres -c "
SELECT datname, xact_commit, xact_rollback, deadlocks
FROM pg_stat_database LIMIT 5;
"
```

### Шаг 4. Роль для резервного копирования

```sql
CREATE ROLE backup_role LOGIN REPLICATION PASSWORD 'backup123';

-- Проверка атрибутов
SELECT rolname, rolreplication FROM pg_authid WHERE rolname = 'backup_role';
```

### Шаг 5. pg_read_all_data

```sql
CREATE ROLE reader_role LOGIN PASSWORD 'reader123';
GRANT pg_read_all_data TO reader_role;

-- Создадим таблицу под другим пользователем
CREATE TABLE sensitive_data(id integer, secret text);
INSERT INTO sensitive_data VALUES (1, 'confidential');
```

```bash
# reader_role может читать все таблицы
psql -U reader_role -d postgres -c "SELECT * FROM sensitive_data;"
```

### Шаг 6. Удаление

```sql
REVOKE pg_read_all_data FROM reader_role;
REVOKE pg_read_all_stats FROM monitoring;
DROP ROLE monitoring;
DROP ROLE backup_role;
DROP ROLE reader_role;
```

## Решение

### Шаг 1: Вывод
```
 Role name     |                          Attributes
---------------+-------------------------------------------------------------
 pg_*          | Cannot login
 pg_monitor    | Cannot login
 pg_read_all_data | Cannot login
 pg_write_all_data | Cannot login
 ...
```

## Контрольные вопросы

1. Почему предопределённые роли не могут входить в систему?
2. В чём разница между `pg_read_all_data` и `SELECT` на все таблицы?
3. Как проверить, какие предопределённые роли доступны?

## Дополнительное задание

Создайте роль `app_admin` с набором привилегий: pg_read_all_data + pg_write_all_data + pg_read_all_stats. Проверьте, что она может выполнять все необходимые операции.
