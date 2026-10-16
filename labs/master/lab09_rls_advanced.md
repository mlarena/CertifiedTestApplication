# Лабораторная работа №9: Продвинутая безопасность с RLS

## Цель
Изучить Row-Level Security: политики USING/FOR, столбцовые ограничения, обход RLS, интеграция с ролями.

## Теория
Row-Level Security (RLS) — механизм ограничения доступа к строкам таблицы на основе политик.

Политики:
- `FOR SELECT` — фильтрует читаемые строки
- `FOR INSERT` — проверяет вставляемые строки
- `FOR UPDATE` — ограничивает обновляемые строки
- `FOR DELETE` — ограничивает удаляемые строки

Каждая политика может быть ограничена ролями: `TO role_name`.

## Задание

### Шаг 1. Базовая настройка RLS

```sql
-- Создание таблицы
CREATE TABLE documents(
    id integer PRIMARY KEY,
    title text,
    content text,
    owner_id integer,
    department text
);

INSERT INTO documents VALUES
    (1, 'Отчёт 1', 'Содержимое 1', 1, 'sales'),
    (2, 'Отчёт 2', 'Содержимое 2', 2, 'sales'),
    (3, 'Отчёт 3', 'Содержимое 3', 3, 'hr'),
    (4, 'Отчёт 4', 'Содержимое 4', 1, 'hr');

-- Создание ролей
CREATE ROLE user1 LOGIN;
CREATE ROLE user2 LOGIN;
CREATE ROLE user3 LOGIN;
GRANT ALL ON documents TO user1, user2, user3;
```

### Шаг 2. Включение RLS

```sql
-- Включение RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Просмотр политик
SELECT * FROM pg_policies WHERE tablename = 'documents';
```

### Шаг 3. Создание политик SELECT

```sql
-- Политика: пользователь видит только свои документы
CREATE POLICY user_select ON documents
    FOR SELECT
    TO user1, user2, user3
    USING (owner_id = current_setting('app.current_user_id')::integer);

-- Проверка
SET app.current_user_id = '1';
SELECT * FROM documents;
-- Видит только id=1 и id=4 (owner_id=1)
```

### Шаг 4. Политика INSERT

```sql
-- Политика: можно вставлять только свои документы
CREATE POLICY user_insert ON documents
    FOR INSERT
    TO user1, user2, user3
    WITH CHECK (owner_id = current_setting('app.current_user_id')::integer);

-- Проверка
SET app.current_user_id = '1';
INSERT INTO documents VALUES (5, 'Отчёт 5', 'Тест', 1, 'sales');
-- OK
INSERT INTO documents VALUES (6, 'Отчёт 6', 'Тест', 2, 'sales');
-- ERROR: new row violates row-level security policy
```

### Шаг 5. Политика UPDATE

```sql
-- Политика: можно обновлять только свои документы
CREATE POLICY user_update ON documents
    FOR UPDATE
    TO user1, user2, user3
    USING (owner_id = current_setting('app.current_user_id')::integer)
    WITH CHECK (owner_id = current_setting('app.current_user_id')::integer);

-- Проверка
SET app.current_user_id = '1';
UPDATE documents SET title = 'Обновлено' WHERE id = 1;
-- OK
UPDATE documents SET title = 'Обновлено' WHERE id = 2;
-- 0 строк (не видит)
```

### Шаг 6. Политика DELETE

```sql
-- Политика: можно удалять только свои документы
CREATE POLICY user_delete ON documents
    FOR DELETE
    TO user1, user2, user3
    USING (owner_id = current_setting('app.current_user_id')::integer);
```

### Шаг 7. Ограничение по столбцам

```sql
-- Ограничение: user1 не может видеть content чужих документов
CREATE POLICY user_select_content ON documents
    FOR SELECT
    TO user1
    USING (owner_id = current_setting('app.current_user_id')::integer
           OR department != 'hr');
```

### Шаг 8. Обход RLS

```sql
-- SUPERUSER и BYPASSRLS обходят RLS
ALTER ROLE user1 BYPASSRLS;

-- Проверка
SET app.current_user_id = '999';
SELECT * FROM documents;
-- Видит все документы
```

### Шаг 9. Принудительное применение к владельцу

```sql
-- Владелец таблицы обходит RLS
-- Принудительное применение к владельцу:
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

## Решение

### Шаг 3: Результат
```
 id | title    | content      | owner_id | department
----+----------+--------------+----------+-----------
  1 | Отчёт 1  | Содержимое 1 |        1 | sales
  4 | Отчёт 4  | Содержимое 4 |        1 | hr
(2 rows)
```

## Контрольные вопросы

1. Чем USING отличается от WITH CHECK?
2. Что произойдёт при отсутствии политики?
3. Кто обходит RLS?
4. Как применить RLS к владельцу таблицы?

## Дополнительное задание

Настройте RLS с многоуровневым доступом: администраторы видят всё, менеджеры — свой отдел, пользователи — только свои документы.