# Лабораторная работа №1: Установка PostgreSQL

## Цель
Научиться устанавливать PostgreSQL из пакетного репозитория и создавать первый кластер баз данных.

## Теория
PostgreSQL — объектно-реляционная система управления базами данных с открытым исходным кодом. При установке из пакетов PostgreSQL Global Development Group (PGDG) пользователь получает актуальную версию сервера с поддержкой всех необходимых компонентов.

Кластер баз данных — это набор баз данных, управляемых одним экземпляром сервера. При установке пакета автоматически создается кластер «main» и инициализируется с помощью утилиты `pg_createcluster` (обертки над `initdb`).

## Задание

### Шаг 1. Добавление репозитория PGDG

```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
```

### Шаг 2. Установка PostgreSQL 16

```bash
sudo apt-get install -y postgresql-16 postgresql-client-16
```

### Шаг 3. Проверка установки

```bash
# Проверяем, что сервер установлен
dpkg -l | grep postgresql-16

# Смотрим структуру каталогов
ls -l /usr/lib/postgresql/16/
```

### Шаг 4. Проверка кластера

```bash
# Список кластеров
pg_lsclusters

# Статус кластера
sudo pg_ctlcluster 16 main status
```

### Шаг 5. Проверка конфигурации сборки

```bash
sudo /usr/lib/postgresql/16/bin/pg_config --configure
```

## Решение

### Шаг 3: Результат

```
dpkg -l | grep postgresql-16
ii  postgresql-16    16.9-1.pgdg24.04+1    amd64   PostgreSQL Cluster Server
ii  postgresql-client-16  16.9-1.pgdg24.04+1  amd64   PostgreSQL Client 16
```

### Шаг 4: Результат

```
pg_lsclusters
Ver Cluster Port Status Owner Data directory                Log file
16  main    5432 online postgres /var/lib/postgresql/16/main  /var/log/postgresql/postgresql-16-main.log
```

## Контрольные вопросы

1. Чем отличается `pg_createcluster` от `initdb`?
2. Где находится каталог данных кластера по умолчанию при установке из пакета?
3. Какой порт используется по умолчанию и как его проверить?

## Дополнительное задание

Установите PostgreSQL из исходных кодов с кастомными параметрами: нестандартный порт 5555 и подсчет контрольных сумм страниц.
