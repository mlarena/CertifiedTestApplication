# Лабораторная работа №10: SSL/TLS конфигурация и аутентификация

## Цель
Настроить SSL/TLS для шифрования соединений, настроить аутентификацию через сертификаты, проверить SSL в pg_hba.conf.

## Теория
PostgreSQL поддерживает SSL/TLS для шифрования соединений между клиентом и сервером. Аутентификация через сертификаты (cert) позволяет использовать клиентские сертификаты вместо паролей.

## Задание

### Шаг 1. Генерация сертификатов

```bash
# Создание каталога для сертификатов
mkdir -p /tmp/ssl_certs
cd /tmp/ssl_certs

# Генерация CA-сертификата
openssl req -new -nodes -text -out ca.csr -keyout ca.key -subj "/CN=PostgreSQL-CA"

# Подпись CA-сертификата
openssl x509 -req -in ca.csr -signkey ca.key -days 365 -out ca.crt

# Генерация серверного ключа и запроса
openssl req -new -nodes -text -out server.csr -keyout server.key -subj "/CN=postgres"

# Подпись серверного сертификата
openssl x509 -req -in server.csr -days 365 -CA ca.crt -CAkey ca.key -out server.crt

# Генерация клиентского ключа и запроса
openssl req -new -nodes -text -out client.csr -keyout client.key -subj "/CN=postgres"

# Подпись клиентского сертификата
openssl x509 -req -in client.csr -days 365 -CA ca.crt -CAkey ca.key -out client.crt

# Проверка
ls -la /tmp/ssl_certs/
```

### Шаг 2. Установка сертификатов на сервер

```bash
# Копирование на сервер
sudo cp /tmp/ssl_certs/server.crt /etc/postgresql/16/main/
sudo cp /tmp/ssl_certs/server.key /etc/postgresql/16/main/
sudo cp /tmp/ssl_certs/ca.crt /etc/postgresql/16/main/

# Настройка прав
sudo chown postgres:postgres /etc/postgresql/16/main/server.*
sudo chown postgres:postgres /etc/postgresql/16/main/ca.crt
sudo chmod 600 /etc/postgresql/16/main/server.key
```

### Шаг 3. Настройка SSL в postgresql.conf

```bash
# Настройка SSL
ALTER SYSTEM SET ssl TO 'on';
ALTER SYSTEM SET ssl_cert_file TO '/etc/postgresql/16/main/server.crt';
ALTER SYSTEM SET ssl_key_file TO '/etc/postgresql/16/main/server.key';
ALTER SYSTEM SET ssl_ca_file TO '/etc/postgresql/16/main/ca.crt';

# Перезагрузка (SSL требует restart)
sudo pg_ctlcluster 16 main restart
```

### Шаг 4. Проверка SSL

```sql
-- Проверка SSL
SHOW ssl;
SHOW ssl_cert_file;
SHOW ssl_key_file;

-- Подключение с проверкой SSL
psql "host=localhost port=5432 dbname=postgres sslmode=require"
```

### Шаг 5. Настройка pg_hba.conf с SSL

```bash
# Добавление SSL-аутентификации в pg_hba.conf
# Тип: hostssl (требует SSL)
echo "hostssl all all 0.0.0.0/0 cert clientcert=verify-full" | \
  sudo tee -a /etc/postgresql/16/main/pg_hba.conf

# Перезагрузка
sudo pg_ctlcluster 16 main reload
```

### Шаг 6. Подключение с клиентским сертификатом

```bash
# Подключение с сертификатом
psql "host=localhost port=5432 dbname=postgres \
  sslmode=verify-full \
  sslcert=/tmp/ssl_certs/client.crt \
  sslkey=/tmp/ssl_certs/client.key \
  sslrootcert=/tmp/ssl_certs/ca.crt"
```

### Шаг 7. Проверка SSL-соединений

```sql
-- Проверка SSL-соединений
SELECT pid, ssl, version, cipher
FROM pg_stat_ssl
WHERE ssl = true;

-- Все соединения с SSL
SELECT pid, usename, ssl, version, cipher
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid);
```

### Шаг 8. Настройка ssl_min_protocol_version

```sql
-- Минимальная версия TLS
ALTER SYSTEM SET ssl_min_protocol_version TO 'TLSv1.2';
SELECT pg_reload_conf();

-- Проверка
SHOW ssl_min_protocol_version;
```

### Шаг 9. Тестирование без SSL

```bash
# Подключение без SSL (должно быть запрещено)
psql "host=localhost port=5432 dbname=postgres sslmode=disable"
-- ERROR: no pg_hba.conf entry for host "..."
```

## Решение

### Шаг 4: Результат
```
 ssl 
-----
 on
(1 row)
```

### Шаг 7: Результат
```
 pid  | ssl | version | cipher
------+-----+---------+------------------
 1234 | t   | TLSv1.3 | TLS_AES_256_GCM_SHA384
```

## Контрольные вопросы

1. Чем hostssl отличается от host в pg_hba.conf?
2. Что делает sslmode=verify-full?
3. Как проверить, что соединение зашифровано?
4. Что произойдёт, если ssl=off?

## Дополнительное задание

Настройте двухстороннюю аутентификацию: сервер проверяет клиентский сертификат, клиент проверяет серверный.