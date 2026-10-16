# Лабораторная работа №1: pg_upgrade с --link/--clone и план Б

## Цель
Научиться обновлять PostgreSQL с минимальным простоем: pg_upgrade --link/--clone, обнаружение проблем (reg-типы, расширения), plan B при --link.

## Теория
pg_upgrade обновляет PostgreSQL без переноса данных — он создаёт новый кластер и связывает его файлы с новым сервером через жёсткие ссылки (--link) или copy-on-write (--clone).

Преимущества: обновление за минуты вместо часов.
Риски: после первого запуска нового кластера старый становится небезопасным для запуска.

Ограничения pg_upgrade:
- Нельзя обновлять, если используются reg* типы в пользовательских таблицах
- Минимальная версия обновления: 8.4+
- Новый кластер должен быть инициализирован с той же локалью и кодировкой

## Задание

### Шаг 1. Подготовка кластеров

```bash
# Старый кластер (симуляция версии 15)
sudo pg_createcluster 15 olddb -- -E UTF8 --locale=C

# Новый кластер (версия 16)
sudo pg_createcluster 16 newdb -- -E UTF8 --locale=C

# Запуск старого
sudo pg_ctlcluster 15 olddb start

# Проверка версий
sudo -u postgres psql -p 5433 -c "SELECT version();"
sudo -u postgres psql -p 5434 -c "SELECT version();"
```

### Шаг 2. Создание тестовых данных

```bash
# Старый кластер: база с таблицами
sudo -u postgres psql -p 5433 -c "CREATE DATABASE testdb;"
sudo -u postgres psql -p 5433 -d testdb -c "
CREATE TABLE t(id integer PRIMARY KEY, name text);
INSERT INTO t SELECT generate_series(1, 100000), md5(random()::text);
CREATE INDEX idx_name ON t(name);
"
```

### Шаг 3. Проверка совместимости

```bash
# Проверка reg-типов (главное ограничение pg_upgrade)
sudo -u postgres psql -p 5433 -d testdb -c "
SELECT tablename, attname, atttypid::regtype
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
WHERE atttypid IN (SELECT oid FROM pg_type WHERE typname LIKE 'reg%')
AND atttypid NOT IN ('regtype'::regtype, 'regclass'::regtype, 'regrole'::regtype);
"

# Проверка расширений
sudo -u postgres psql -p 5433 -d testdb -c "SELECT * FROM pg_extension;"
```

### Шаг 4. Запуск pg_upgrade

```bash
# Выделенный каталог для логов
mkdir -p /tmp/pg_upgrade_logs

# Запуск с --link (жёсткие ссылки)
sudo -u postgres /usr/lib/postgresql/16/bin/pg_upgrade \
  --old-datadir=/var/lib/postgresql/15/olddb \
  --new-datadir=/var/lib/postgresql/16/newdb \
  --old-bindir=/usr/lib/postgresql/15/bin \
  --new-bindir=/usr/lib/postgresql/16/bin \
  --link \
  --jobs=4 \
  --logdir=/tmp/pg_upgrade_logs \
  --check

# Запуск с фактическим обновлением (без --check)
sudo -u postgres /usr/lib/postgresql/16/bin/pg_upgrade \
  --old-datadir=/var/lib/postgresql/15/olddb \
  --new-datadir=/var/lib/postgresql/16/newdb \
  --old-bindir=/usr/lib/postgresql/15/bin \
  --new-bindir=/usr/lib/postgresql/16/bin \
  --link \
  --jobs=4 \
  --logdir=/tmp/pg_upgrade_logs
```

### Шаг 5. План Б — останов и запуск

```bash
# ВАЖНО: после запуска нового кластера старый НЕЛЬЗЯ запускать!
sudo pg_ctlcluster 16 newdb start
sudo -u postgres psql -p 5434 -c "SELECT count(*) FROM testdb.t;"

# Если что-то пошло не так — ОСТАВЛЯЕМ СТАРЫЙ КЛАСТЕР РАБОТАТЬ
# НЕ запускаем новый кластер повторно
# Используем старый как план Б
sudo pg_ctlcluster 15 olddb status
```

### Шаг 6. Сбор статистики

```sql
-- Запуск vacuum с анализом
sudo -u postgres psql -p 5434 -d testdb -c "VACUUM ANALYZE;"

-- Параллельный vacuum
sudo -u postgres vacuumdb -p 5434 -d testdb --analyze-in-stages -j 4
```

### Шаг 7. Очистка

```bash
# Удаление старого кластера
sudo pg_ctlcluster 15 olddb stop
sudo pg_dropcluster 15 olddb
```

## Решение

### Шаг 4: Результат
```
Performing Consistency Checks
-----------------------------
Checking cluster versions                                   ok
Checking database user is a superuser                       ok
...
Upgrade could complete successfully
```

## Контрольные вопросы

1. Почему после --link нельзя запускать старый кластер?
2. Какие reg-типы запрещают pg_upgrade?
3. Чем --clone отличается от --link?
4. Зачем нужен --check?

## Дополнительное задание

Настройте pg_upgrade с --clone на файловом сервере XFS с поддержкой copy-on-write.