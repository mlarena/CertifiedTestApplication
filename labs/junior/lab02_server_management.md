# Лабораторная работа №2: Управление сервером

## Цель
Освоить управление экземпляром PostgreSQL: запуск, останов, перезапуск, перечитывание конфигурации, просмотр журнала сообщений.

## Теория
Управление сервером PostgreSQL осуществляется утилитой `pg_ctl` (или оберткой `pg_ctlcluster` в Ubuntu). Основные операции: запуск (`start`), останов (`stop`), перезапуск (`restart`), перечитывание конфигурации (`reload`), получение статуса (`status`).

Режимы останова:
- `fast` (по умолчанию) — выполняет контрольную точку и останавливается
- `immediate` — имитирует сбой, при рестарте потребуется восстановление
- `smart` — ждет завершения всех соединений (для обслуживания)

## Задание

### Шаг 1. Просмотр статуса сервера

```bash
sudo pg_ctlcluster 16 main status
```

### Шаг 2. Останов сервера в режиме fast

```bash
sudo pg_ctlcluster 16 main stop
pg_lsclusters
```

### Шаг 3. Запуск сервера

```bash
sudo pg_ctlcluster 16 main start
pg_lsclusters
```

### Шаг 4. Перезапуск сервера

```bash
sudo pg_ctlcluster 16 main restart
```

### Шаг 5. Перечитывание конфигурации (без останова)

```bash
# Или через SQL:
psql -U postgres -c "SELECT pg_reload_conf();"
```

### Шаг 6. Просмотр журнала сообщений

```bash
# Последние 20 строк журнала
tail -n 20 /var/log/postgresql/postgresql-16-main.log
```

### Шаг 7. Останов в режиме immediate (имитация сбоя)

```bash
sudo pg_ctlcluster 16 main stop -m immediate --skip-systemctl-redirect
# Запуск с восстановлением
sudo pg_ctlcluster 16 main start
# Проверяем журнал — видим automatic recovery
tail -n 15 /var/log/postgresql/postgresql-16-main.log
```

## Решение

### Шаг 1: Результат
```
pg_ctl: server is running (PID: 3452)
/usr/lib/postgresql/16/bin/postgres "-D" "/var/lib/postgresql/16/main" "-c"
"config_file=/etc/postgresql/16/main/postgresql.conf"
```

### Шаг 7: Журнал после immediate
```
2025-06-23 23:31:47.695 LOG: database system was not properly shut down;
automatic recovery in progress
2025-06-23 23:31:47.720 LOG: redo is not required
2025-06-23 23:31:47.751 LOG: checkpoint starting: end-of-recovery immediate wait
2025-06-23 23:31:47.848 LOG: database system is ready to accept connections
```

## Контрольные вопросы

1. Чем режим `fast` отличается от `immediate`?
2. Что такое контрольная точка и зачем она нужна при останове?
3. Как проверить, что сервер восстановился после аварийной остановки?

## Дополнительное задание

Найдите PID процесса postmaster через файл `postmaster.pid` и найдите все дочерние процессы через `ps`.
