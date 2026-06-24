# Лабораторная работа №10: pg_hba.conf

## Цель
Освоить настройку аутентификации через pg_hba.conf: методы, приоритет правил, отображение ролей.

## Теория
`pg_hba.conf` определяет, кто может подключаться к серверу и как аутентифицируется. Строки проверяются сверху вниз; используется первое совпадение. Методы: trust, reject, scram-sha-256, md5, peer, cert.

## Задание

### Шаг 1. Просмотр текущих правил

```sql
SELECT type, database, user_name, address, auth_method
FROM pg_hba_file_rules()
ORDER BY rule_number;
```

### Шаг 2. Создание тестовых ролей

```sql
CREATE ROLE test_user LOGIN PASSWORD 'test123';
CREATE ROLE test_admin LOGIN PASSWORD 'admin123';
```

### Шаг 3. Добавление правила для test_user

```bash
# Добавляем строку в pg_hba.conf
echo "host all test_user 127.0.0.1/32 scram-sha-256" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf
```

```sql
SELECT pg_reload_conf();
```

```bash
# Проверяем подключение
psql -h localhost -U test_user -d postgres -c "SELECT current_user;"
```

### Шаг 4. Отображение ролей (peer + pg_ident.conf)

```bash
# Добавляем отображение
echo "mymap student test_user" | sudo tee -a /etc/postgresql/16/main/pg_ident.conf

# Добавляем правило peer
echo "local all test_user peer map=mymap" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf
```

```sql
SELECT pg_reload_conf();
```

```bash
# Проверяем
psql -U test_user -d postgres -c "SELECT current_user;"
```

### Шаг 5. Запрет доступа

```bash
# Добавляем reject для тестовой роли
echo "local all test_admin reject" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf
```

```sql
SELECT pg_reload_conf();
```

```bash
# Проверяем
psql -U test_admin -d postgres -c "SELECT current_user;"
-- FATAL: pg_hba.conf rejects connection
```

### Шаг 6. Просмотр правил

```sql
SELECT rule_number, type, database, user_name, address, auth_method, error
FROM pg_hba_file_rules
WHERE auth_method IS NOT NULL
ORDER BY rule_number;
```

## Решение

### Шаг 6: Результат
```
 rule_number | type  |    database     | user_name |  address   | auth_method  | error
-------------+-------+-----------------+-----------+------------+--------------+-------
           1 | local | {all}           | {student} |            | trust        |
           2 | host  | {all}           | {all}     | 127.0.0.1  | scram-sha-256|
           3 | host  | {all}           | {all}     | ::1        | scram-sha-256|
           4 | local | {all}           | {test_user}|           | peer         |
           5 | local | {all}           | {test_admin}|          | reject       |
(5 rows)
```

## Контрольные вопросы

1. Почему записи pg_hba.conf проверяются сверху вниз?
2. Какой метод аутентификации самый безопасный?
3. Зачем нужен `pg_ident.conf`?

## Дополнительное задание

Настройте SSL-аутентификацию и проверьте подключение с сертификатом.
