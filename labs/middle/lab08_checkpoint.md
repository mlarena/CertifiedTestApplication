# Лабораторная работа №8: Контрольные точки

## Цель
Изучить механизм контрольных точек (checkpoint): назначение, влияние на производительность, восстановление после сбоя.

## Теория
Контрольная точка — процесс принудительного сброса всех грязных буферов на диск. Это гарантирует, что все изменения до момента КТ находятся на диске. КТ также ограничивает размер WAL, необходимый для восстановления. При сбое восстановление начинается с последней завершённой КТ.

## Задание

### Шаг 1. Ручное выполнение КТ

```sql
CHECKPOINT;

\! tail -n 5 /var/log/postgresql/postgresql-16-main.log | grep checkpoint
```

### Шаг 2. Параметры КТ

```sql
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name IN (
    'checkpoint_timeout',
    'checkpoint_completion_target',
    'max_wal_size',
    'min_wal_size'
) \gx
```

### Шаг 3. Статистика КТ

```sql
SELECT checkpoints_timed, checkpoints_req, buffers_checkpoint,
       buffers_backend, maxwritten
FROM pg_stat_bgwriter;
```

### Шаг 4. Восстановление после «сбоя»

```bash
# Находим PID postmaster
sudo head -n 1 /var/lib/postgresql/16/main/postmaster.pid

# Отправляем SIGQUIT (имитация сбоя)
sudo kill -QUIT <PID>

# Запускаем сервер
sudo pg_ctlcluster 16 main start

# Проверяем журнал восстановления
\! grep -i "recovery\|checkpoint\|redo" /var/log/postgresql/postgresql-16-main.log | tail -n 10
```

## Решение

### Шаг 1: Результат
```
LOG: checkpoint starting: immediate
LOG: checkpoint complete: wrote 5 buffers (0.0%); 0
WAL file(s) added, 0 removed, 0 recycled; write=0.112 s, sync=0.032 s
```

### Шаг 3: Результат
```
 checkpoints_timed | checkpoints_req | buffers_checkpoint | buffers_backend
-------------------+-----------------+--------------------+----------------
                 5 |               0 |               1234 |            5678
(1 row)
```

## Контрольные вопросы

1. Что такое `checkpoints_req` и когда они возникают?
2. Как `checkpoint_completion_target` влияет на нагрузку ввода-вывода?
3. Почему после immediate-остановки сервер выполняет восстановление?

## Дополнительное задание

Настройте `checkpoint_timeout = 15min` и `max_wal_size = 2GB`. Выполните серию обновлений и наблюдайте за частотой контрольных точек в журнале.
