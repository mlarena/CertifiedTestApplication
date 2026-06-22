# Лабораторная работа №13: Row Level Security

## Цель
Научиться настраивать безопасность на уровне строк (RLS): политики, ограничение доступа к данным в зависимости от роли пользователя.

## Теория
Row Level Security (RLS) позволяет ограничивать, какие строки таблицы видны конкретному пользователю. Политики определяются через `CREATE POLICY` и применяются через `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.

## Задание

### Шаг 1. Создание окружения

```sql
CREATE DATABASE lab_rls;
\c lab_rls

CREATE ROLE tenant_a LOGIN PASSWORD 'a123';
CREATE ROLE tenant_b LOGIN PASSWORD 'b123';
CREATE ROLE admin_rls LOGIN PASSWORD 'admin123' SUPERUSER;

CREATE TABLE documents(
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant text NOT NULL,
    title text,
    data text
);

INSERT INTO documents(tenant, title, data) VALUES
('tenant_a', 'Doc A1', 'data a1'),
('tenant_a', 'Doc A2', 'data a2'),
('tenant_b', 'Doc B1', 'data b1'),
('tenant_b', 'Doc B2', 'data b2');
```

### Шаг 2. Включение RLS

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
```

### Шаг 3. Создание политики

```sql
-- Каждый tenant видит только свои документы
CREATE POLICY tenant_isolation ON documents
    FOR ALL
    USING (tenant = current_user);
```

### Шаг 4. Проверка

```bash
# tenant_a видит только свои
psql -U tenant_a -d lab_rls -c "SELECT * FROM documents;"

# tenant_b видит только свои
psql -U tenant_b -d lab_rls -c "SELECT * FROM documents;"
```

### Шаг 5. Принудительное включение

```sql
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

```bash
# Даже суперпользователь под другой ролью
psql -U tenant_a -d lab_rls -c "SELECT * FROM documents;"
```

### Шаг 6. Политика для INSERT/UPDATE

```sql
-- Разрешаем вставку только в свой tenant
CREATE POLICY tenant_insert ON documents
    FOR INSERT
    WITH CHECK (tenant = current_user);

-- Разрешаем обновление только своих
CREATE POLICY tenant_update ON documents
    FOR UPDATE
    USING (tenant = current_user)
    WITH CHECK (tenant = current_user);
```

### Шаг 7. Удаление политики

```sql
DROP POLICY tenant_isolation ON documents;
DROP POLICY tenant_insert ON documents;
DROP POLICY tenant_update ON documents;
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
```

## Решение

### Шаг 4: Результат
```
-- tenant_a:
 id | tenant  | title  | data
----+---------+--------+--------
  1 | tenant_a | Doc A1 | data a1
  2 | tenant_a | Doc A2 | data a2
(2 rows)

-- tenant_b:
 id | tenant  | title  | data
----+---------+--------+--------
  3 | tenant_b | Doc B1 | data b1
  4 | tenant_b | Doc B2 | data b2
(2 rows)
```

## Контрольные вопросы

1. Как `FORCE ROW LEVEL SECURITY` влияет на суперпользователя?
2. Что такое `USING` и `WITH CHECK` в политике?
3. Как RLS влияет на производительность?

## Дополнительное задание

Настройте политику, которая разрешает читать все строки, но изменять только свои.
