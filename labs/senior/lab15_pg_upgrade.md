# Лабораторная работа №15: Обновление PostgreSQL (pg_upgrade)

## Цель
Изучить методы обновления PostgreSQL: pg_upgrade для обновления основной версии, логическая репликация для обновления без простоя.

## Теория
pg_upgrade позволяет обновить кластер PostgreSQL на новую основную версию с минимальным простоем. Альтернатива — логическая репликация: настраивается между старым и новым серверами, данные синхронизируются, затем клиенты переключаются.

## Задание

### Шаг 1. Проверка текущей версии

```sql
SHOW server_version;
SELECT version();
```

### Шаг 2. pg_upgrade — проверка совместимости

```bash
# Останавливаем старый сервер
sudo pg_ctlcluster 16 main stop

# Проверяем (dry run)
sudo -u postgres /usr/lib/postgresql/17/bin/pg_upgrade \
    --old-datadir=/var/lib/postgresql/16/main \
    --new-datadir=/var/lib/postgresql/17/main \
    --old-bindir=/usr/lib/postgresql/16/bin \
    --new-bindir=/usr/lib/postgresql/17/bin \
    --check
```

### Шаг 3. pg_upgrade — выполнение

```bash
sudo -u postgres /usr/lib/postgresql/17/bin/pg_upgrade \
    --old-datadir=/var/lib/postgresql/16/main \
    --new-datadir=/var/lib/postgresql/17/main \
    --old-bindir=/usr/lib/postgresql/16/bin \
    --new-bindir=/usr/lib/postgresql/17/bin \
    --link
```

### Шаг 4. Пост-обновление

```bash
# Перезапуск на новой версии
sudo pg_ctlcluster 17 main start

# Обновление статистики
sudo -u postgres vacuumdb --all --analyze-in-stages
```

### Шаг 5. Альтернатива: логическая репликация для обновления

```sql
-- На старом сервере (16): wal_level = logical
ALTER SYSTEM SET wal_level = 'logical';
-- Перезапуск

-- Создаём публикации для всех таблиц
CREATE PUBLICATION all_tables FOR ALL TABLES;

-- На новом сервере (17): подписываемся
CREATE SUBSCRIPTION all_tables_sub
CONNECTION 'port=5432 user=student dbname=lab_update'
PUBLICATION all_tables;

-- Ждём начальную синхронизацию
SELECT * FROM pg_stat_subscription;

-- Переключаем клиентов на новый сервер
```

## Решение

### Шаг 1: Результат
```
SHOW server_version;
 server_version
----------------
 16.9
(1 row)
```

## Контрольные вопросы

1. Что делает флаг `--link` в pg_upgrade?
2. Как pg_upgrade влияет на время простоя?
3. В каких случаях логическая репликация предпочтительнее pg_upgrade?

## Дополнительное задание

Сравните время обновления через pg_upgrade и через логическую репликацию на базе данных размером 10 ГБ.
