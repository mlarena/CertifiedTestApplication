"""Middle test generator — 80 questions on PostgreSQL best practices and certification topics."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import A, Q, QN, dump_json

Qs = []

# ========== Topic 01: Установка и управление сервером ==========
Qs.append(Q("Какой пользователь ОС должен управлять каталогом кластера PostgreSQL?",
    [A("postgres", True), A("root", False), A("any", False), A("admin", False)]))

Qs.append(Q("Что делает команда 'sudo pg_ctlcluster 16 main restart'?",
    [A("Перезапускает кластер PostgreSQL 16 с именем main", True),
     A("Останавливает кластер PostgreSQL 16 с именем main", False),
     A("Запускает новый кластер PostgreSQL 16 с именем main", False),
     A("Перечитывает конфигурацию без перезапуска", False)]))

Qs.append(Q("Какой параметр в postgresql.conf задаёт прослушиваемые интерфейсы?",
    [A("listen_addresses", True), A("bind_address", False),
     A("server_address", False), A("port", False)]))

Qs.append(Q("Какие утилиты входят в стандартную поставку PostgreSQL?",
    [A("pg_basebackup", True), A("pg_dump", True),
     A("pg_ctl", True), A("pgadmin", False),
     A("pgbadger", False), A("pgbench", True)]))

Qs.append(Q("Какой параметр initdb влияет на способ проверки подлинности паролей?",
    [A("--pwfile", True), A("--auth-host", False),
     A("--password-file", False), A("--init-passwd", False)]))

# ========== Topic 02: Использование psql ==========
Qs.append(Q("Какая переменная psql показывает текущую транзакцию в приглашении?",
    [A("%R", True), A("%T", False), A("$", False), A("%X", False)]))

Qs.append(Q("Как записать вывод запроса в файл прямо из psql?",
    [A("\\g (format=csv) filename.csv", True),
     A("\\output filename.csv", False),
     A("\\w filename.csv", False),
     A("\\copy query to filename.csv", False)]))

Qs.append(Q("Какой командой psql можно вывести план выполнения запроса?",
    [A("\\explain [query]", True),
     A("EXPLAIN [query]", True),
     A("\\plan [query]", False),
     A("\\show plan [query]", False),
     A("\\analyze [query]", False)]))

Qs.append(Q("Как работает переменная ON_ERROR_ROLLBACK?",
    [A("Перед каждой командой SQL в транзакции устанавливается SAVEPOINT, при ошибке — откат к нему", True),
     A("Автоматически фиксирует транзакцию при ошибке", False),
     A("Прерывает все транзакции при первой ошибке", False),
     A("Отключает режим автокоммита", False)]))

Qs.append(Q("Какие переменные psql настраивают внешний вид приглашения?",
    [A("PROMPT1", True), A("PROMPT2", True),
     A("PROMPT3", True), A("PROMPT4", False),
     A("PROMPT_COMMAND", False)]))

# ========== Topic 03: Конфигурирование сервера ==========
Qs.append(Q("Какой параметр отвечает за максимальное количество дочерних процессов autovacuum?",
    [A("autovacuum_max_workers", True),
     A("max_autovacuum_workers", False),
     A("autovacuum_worker_limit", False),
     A("max_vacuum_processes", False)]))

Qs.append(Q("Какие параметры требуют только перезапуска сервера (context = postmaster)?",
    [A("shared_buffers", True), A("max_connections", True),
     A("work_mem", False), A("log_min_duration", False),
     A("listen_addresses", True), A("maintenance_work_mem", False)]))

Qs.append(Q("Какой параметр ограничивает размер WAL, который может быть сгенерирован между контрольными точками?",
    [A("max_wal_size", True),
     A("wal_keep_size", False),
     A("checkpoint_completion_target", False),
     A("min_wal_size", False)]))

Qs.append(Q("Какой из параметров влияет на планировщик запросов?",
    [A("effective_cache_size", True),
     A("shared_buffers", False),
     A("work_mem", False),
     A("max_wal_size", False)]))

Qs.append(Q("Какой параметр включает сбор статистики вызовов пользовательских функций?",
    [A("track_functions", True),
     A("track_counts", False),
     A("pg_stat_functions", False),
     A("stats_functions", False)]))

# ========== Topic 04: Общее устройство ==========
Qs.append(Q("Какие свойства ACID гарантирует PostgreSQL?",
    [A("Atomicity", True), A("Consistency", True),
     A("Isolation", True), A("Durability", True),
     A("Availability", False), A("Scalability", False)]))

Qs.append(Q("Что такое postmaster в PostgreSQL?",
    [A("Главный процесс сервера, который запускает и контролирует все остальные процессы", True),
     A("Пользователь, который управляет сервером", False),
     A("Процесс, отвечающий за запись WAL", False),
     A("Фоновый процесс очистки", False)]))

Qs.append(Q("Что такое backend-процесс?",
    [A("Обслуживающий процесс, создаваемый для каждого подключения клиента", True),
     A("Фоновый процесс, записывающий данные на диск", False),
     A("Демон, принимающий сетевые соединения", False),
     A("Внутренний процесс планирования запросов", False)]))

Qs.append(Q("Какие из перечисленных типов индексов поддерживаются в PostgreSQL?",
    [A("B-tree", True), A("Hash", True), A("GiST", True),
     A("GIN", True), A("BRIN", True),
     A("Bitmap", False), A("Cluster", False)]))

Qs.append(Q("Какой размер страницы в PostgreSQL?",
    [A("8 КБ (по умолчанию)", True), A("4 КБ", False),
     A("16 КБ", False), A("32 КБ", False)]))

# ========== Topic 05: Изоляция и MVCC ==========
Qs.append(Q("Какой уровень изоляции допускает phantom reads?",
    [A("Read Committed", True), A("Repeatable Read", False),
     A("Serializable", False), A("Read Uncommitted", False)]))

Qs.append(Q("Какой уровень изоляции строит снимок данных на момент начала первого оператора транзакции?",
    [A("Repeatable Read", True), A("Read Committed", False),
     A("Serializable", False), A("Read Uncommitted", False)]))

Qs.append(Q("Что такоеxmin в контексте MVCC?",
    [A("Номер транзакции, которая создала данную версию строки", True),
     A("Номер транзакции, которая удалила данную версию строки", False),
     A("Время создания версии строки в Unix-формате", False),
     A("Идентификатор процесса, создавшего версию строки", False)]))

Qs.append(Q("Что такое xmax?",
    [A("Номер транзакции, которая удалила или изменила версию строки (0 если версия актуальна)", True),
     A("Номер транзакции, создавшей версию строки", False),
     A("Максимальный номер транзакции", False),
     A("Идентификатор блокировки строки", False)]))

Qs.append(Q("Какие аномалии допускает уровень Read Committed?",
    [A("Non-repeatable reads", True), A("Phantom reads", True),
     A("Dirty reads", False), A("Lost updates", False)]))

# ========== Topic 06: Очистка (VACUUM) ==========
Qs.append(Q("Какие параметры автоочистки определяют порог запуска для таблиц?",
    [A("autovacuum_vacuum_threshold", True),
     A("autovacuum_vacuum_scale_factor", True),
     A("autovacuum_analyze_threshold", True),
     A("autovacuum_vacuum_cost_delay", False),
     A("autovacuum_max_workers", False)]))

Qs.append(Q("Что такое горизонт очистки (vacuum horizon)?",
    [A("Номер транзакции, до которого все версии строк гарантированно не видны ни в одном снимке", True),
     A("Момент времени, когда была выполнена последняя очистка", False),
     A("Размер таблицы, после которого запускается очистка", False),
     A("Уровень изоляции, при котором очистка невозможна", False)]))

Qs.append(Q("Какие задачи выполняет VACUUM?",
    [A("Вычистка мёртвых версий строк", True),
     A("Обновление карты видимости", True),
     A("Обновление карты свободного пространства", True),
     A("Уменьшение размера файла таблицы", False),
     A("Перестроение индексов", False),
     A("Анализ для планировщика", False)]))

Qs.append(Q("Что делает команда ANALYZE?",
    [A("Собирает статистику о данных в таблицах для планировщика запросов", True),
     A("Вычищает мёртвые версии строк", False),
     A("Перестраивает индексы", False),
     A("Полностью блокирует таблицу на время выполнения", False)]))

Qs.append(Q("Какая команда перестраивает индексы без блокировки таблицы на запись?",
    [A("REINDEX TABLE CONCURRENTLY", True),
     A("VACUUM FULL", False),
     A("REINDEX TABLE", False),
     A("CLUSTER", False)]))

# ========== Topic 07: Буферный кеш и WAL ==========
Qs.append(Q("Какой размер файла WAL по умолчанию?",
    [A("16 МБ", True), A("8 МБ", False),
     A("32 МБ", False), A("64 МБ", False)]))

Qs.append(Q("Какие из перечисленных процессов PostgreSQL связаны с буферным кешем?",
    [A("checkpointer", True), A("background writer", True),
     A("walwriter", True), A("autovacuum launcher", False),
     A("logical replication launcher", False)]))

Qs.append(Q("Что такое «грязный» (dirty) буфер?",
    [A("Буфер, изменённый в памяти, но ещё не записанный на диск", True),
     A("Буфер с повреждённой контрольной суммой", False),
     A("Буфер, вытесненный из кеша", False),
     A("Буфер, зарезервированный под WAL", False)]))

Qs.append(Q("Какие объекты НЕ защищены WAL?",
    [A("Временные таблицы", True),
     A("Нежурналируемые (UNLOGGED) таблицы", True),
     A("Индексы", False),
     A("Обычные таблицы", False),
     A("Статус транзакций (clog)", False)]))

Qs.append(Q("Какой параметр определяет, как часто выполняется контрольная точка?",
    [A("checkpoint_timeout", True),
     A("max_wal_size", False),
     A("checkpoint_completion_target", False),
     A("wal_writer_delay", False)]))

# ========== Topic 08: Базы данных и схемы ==========
Qs.append(Q("Что произойдёт при удалении базы данных?",
    [A("Все схемы и объекты внутри будут удалены", True),
     A("Будут удалены только таблицы, но представления останутся", False),
     A("База данных будет переведена в режим только для чтения", False),
     A("Объекты переместятся в схему public", False)]))

Qs.append(Q("Какие привилегии есть у схемы?",
    [A("CREATE", True), A("USAGE", True),
     A("SELECT", False), A("INSERT", False),
     A("TEMPORARY", False), A("CONNECT", False)]))

Qs.append(Q("Что такое search_path?",
    [A("Список схем, в которых сервер ищет объекты по короткому имени", True),
     A("Путь к файлам базы данных на диске", False),
     A("Приоритет индексов при выполнении запроса", False),
     A("Каталог для временных файлов", False)]))

Qs.append(Q("Что делает команда ALTER TABLE ... SET SCHEMA?",
    [A("Перемещает таблицу в другую схему (логическая операция, данные не перемещаются)", True),
     A("Физически перемещает файлы данных в другой каталог", False),
     A("Меняет владельца таблицы", False),
     A("Создаёт копию таблицы в новой схеме", False)]))

Qs.append(Q("Какая схема содержит предопределённые функции и операторы?",
    [A("pg_catalog", True), A("public", False),
     A("information_schema", False), A("pg_toast", False)]))

# ========== Topic 09: Системный каталог ==========
Qs.append(Q("Какая таблица системного каталога хранит информацию о базах данных?",
    [A("pg_database", True), A("pg_db", False),
     A("sys_database", False), A("pg_tablespace", False)]))

Qs.append(Q("Какие представления pg_stat_* являются временными?",
    [A("pg_stat_activity", True), A("pg_stat_database", True),
     A("pg_stat_all_tables", True), A("pg_stat_reset()", False),
     A("pg_stat_tmp/", False)]))

Qs.append(Q("Что означает relpersistence = 'u' в pg_class?",
    [A("Unlogged — нежурналируемая таблица", True),
     A("Temporary — временная таблица", False),
     A("Permanent — обычная таблица", False),
     A("View — представление", False)]))

Qs.append(Q("Какие столбцы есть в pg_class?",
    [A("relname", True), A("relkind", True),
     A("relnamespace", True), A("relfilenode", True),
     A("relowner", True), A("reltuples", True),
     A("relsize", False), A("relpath", False)]))

Qs.append(Q("Какой тип объекта соответствует relkind = 'm'?",
    [A("Материализованное представление", True),
     A("Обычное представление", False),
     A("Таблица", False),
     A("Индекс", False)]))

# ========== Topic 10: Табличные пространства ==========
Qs.append(Q("Что происходит при переносе таблицы в другое табличное пространство?",
    [A("Физическое копирование файлов данных, полная блокировка таблицы на время переноса", True),
     A("Логическая операция — меняется только ссылка в системном каталоге", False),
     A("Перенос происходит мгновенно, без блокировок", False),
     A("Таблица становится временной", False)]))

Qs.append(Q("Какой параметр задаёт табличное пространство по умолчанию для новых объектов?",
    [A("default_tablespace", True),
     A("temp_tablespaces", False),
     A("tablespace", False),
     A("pg_default", False)]))

Qs.append(Q("Какие объекты могут быть размещены в пользовательском табличном пространстве?",
    [A("Таблицы", True), A("Индексы", True),
     A("База данных целиком", True),
     A("Файлы WAL", False),
     A("Объекты системного каталога кластера", False)]))

Qs.append(Q("Какая команда перемещает все таблицы из одного табличного пространства в другое?",
    [A("ALTER TABLE ALL IN TABLESPACE ts_name SET TABLESPACE new_ts", True),
     A("MOVE TABLESPACE ts_name TO new_ts", False),
     A("ALTER TABLESPACE ts_name RENAME TO new_ts", False),
     A("REASSIGN OWNED BY ts_name", False)]))

Qs.append(Q("В каком каталоге PostgreSQL хранит символические ссылки на пользовательские табличные пространства?",
    [A("PGDATA/pg_tblspc/", True),
     A("PGDATA/base/", False),
     A("PGDATA/global/", False),
     A("PGDATA/pg_default/", False)]))

# ========== Topic 11: Организация данных (файлы, TOAST) ==========
Qs.append(Q("Какой максимальный размер версии строки без TOAST?",
    [A("Около 2 КБ (доля от страницы 8 КБ)", True),
     A("8 КБ (полная страница)", False),
     A("1 МБ", False),
     A("64 КБ", False)]))

Qs.append(Q("Какие стратегии хранения доступны для TOAST?",
    [A("plain", True), A("extended", True),
     A("external", True), A("main", True),
     A("inline", False), A("compressed", False)]))

Qs.append(Q("Какие методы сжатия поддерживает TOAST?",
    [A("pglz", True), A("lz4", True),
     A("zstd", False), A("gzip", False),
     A("bzip2", False)]))

Qs.append(Q("Какие слои (forks) существуют у индекса?",
    [A("main", True), A("fsm", True),
     A("vm", False), A("init", False)]))

Qs.append(Q("Какая функция возвращает размер таблицы с учётом индексов и TOAST?",
    [A("pg_total_relation_size()", True),
     A("pg_relation_size()", False),
     A("pg_table_size()", False),
     A("pg_size_pretty()", False)]))

# ========== Topic 12: Мониторинг ==========
Qs.append(Q("Какие представления содержат информацию об активности сервера?",
    [A("pg_stat_activity", True), A("pg_stat_replication", True),
     A("pg_stat_progress_vacuum", True),
     A("pg_stat_all_tables", True),
     A("pg_stat_progress_basebackup", True),
     A("pg_stat_server", False)]))

Qs.append(Q("Какой параметр включает запись сообщений сервера в файл?",
    [A("logging_collector = on", True),
     A("log_destination = stderr", False),
     A("log_to_file = on", False),
     A("log_directory = 'pg_log'", False)]))

Qs.append(Q("Какие форматы вывода журнала поддерживаются?",
    [A("stderr", True), A("csvlog", True),
     A("jsonlog", True),
     A("syslog", True),
     A("eventlog", True),
     A("xmllog", False)]))

Qs.append(Q("Какая функция возвращает массив PID процессов, блокирующих данный процесс?",
    [A("pg_blocking_pids(pid)", True),
     A("pg_locks.blocking_pids", False),
     A("pg_stat_activity.blocking_pids", False),
     A("pg_blocking_locks()", False)]))

Qs.append(Q("Что означает состояние 'idle in transaction' в pg_stat_activity?",
    [A("Сеанс начал транзакцию, но в настоящее время не выполняет запрос; транзакция остаётся открытой", True),
     A("Сеанс простаивает вне транзакции", False),
     A("Процесс завершён", False),
     A("Запрос выполняется", False)]))

# ========== Topic 13: Управление доступом ==========
Qs.append(Q("Какие атрибуты может иметь роль?",
    [A("LOGIN", True), A("SUPERUSER", True),
     A("CREATEDB", True), A("CREATEROLE", True),
     A("REPLICATION", True), A("BYPASSRLS", True),
     A("CONNECT", False), A("GRANT", False)]))

Qs.append(Q("Какой метод аутентификации в pg_hba.conf безусловно запрещает подключение?",
    [A("reject", True), A("trust", False),
     A("scram-sha-256", False), A("md5", False)]))

Qs.append(Q("Какие предопределённые роли существуют в PostgreSQL?",
    [A("pg_read_all_data", True), A("pg_write_all_data", True),
     A("pg_monitor", True), A("pg_read_all_settings", True),
     A("pg_read_server_files", True),
     A("pg_admin", False),
     A("pg_superuser", False)]))

Qs.append(Q("Что делает SECURITY DEFINER у функции?",
    [A("Функция выполняется с правами своего владельца, а не вызывающего", True),
     A("Функция выполняется с правами вызывающего", False),
     A("Функция не может обращаться к таблицам", False),
     A("Функция шифрует данные", False)]))

Qs.append(Q("Как настроить Row-Level Security (RLS)?",
    [A("ALTER TABLE ... ENABLE ROW LEVEL SECURITY; CREATE POLICY ... ON TABLE ...", True),
     A("GRANT SELECT ON TABLE ... TO ...", False),
     A("CREATE VIEW ... WHERE ...", False),
     A("ALTER ROLE ... SET RLS = on", False)]))

# ========== Topic 14: Резервное копирование ==========
Qs.append(Q("Какие форматы вывода поддерживает pg_dump?",
    [A("plain (SQL-скрипт)", True),
     A("custom (архив с оглавлением)", True),
     A("tar", True),
     A("directory", True),
     A("binary", False),
     A("xml", False)]))

Qs.append(Q("Какие объекты НЕ сохраняются в pg_dump базы данных?",
    [A("Роли", True), A("Табличные пространства", True),
     A("Таблицы", False), A("Индексы", False),
     A("Представления", False)]))

Qs.append(Q("Что такое непрерывная архивация WAL?",
    [A("Автоматическое сохранение файлов WAL в архив для восстановления на произвольный момент времени", True),
     A("Резервное копирование всей БД в архивный файл", False),
     A("Перемещение WAL в архивное хранилище", False),
     A("Шифрование WAL-файлов", False)]))

Qs.append(Q("Какой параметр включает непрерывную архивацию WAL?",
    [A("archive_mode = on", True),
     A("wal_level = logical", False),
     A("archive_command", False),
     A("restore_command", False)]))

Qs.append(Q("Какая команда восстанавливает из резервной копии на определённый момент времени?",
    [A("recovery_target_time = '...' в recovery.signal", True),
     A("pg_restore --at-time '...'", False),
     A("RESTORE DATABASE ... TO '...'", False),
     A("pg_basebackup --recovery-time", False)]))

# ========== Topic 15: Физическая репликация ==========
Qs.append(Q("Какой параметр wal_level необходим для физической репликации?",
    [A("replica", True), A("minimal", False),
     A("logical", False), A("archive", False)]))

Qs.append(Q("Какие команды разрешены на реплике в режиме hot standby?",
    [A("SELECT", True), A("SET", True),
     A("BEGIN/COMMIT", True), A("pg_basebackup", True),
     A("INSERT", False), A("VACUUM", False),
     A("CREATE TABLE", False), A("GRANT", False)]))

Qs.append(Q("Какой параметр определяет, будет ли реплика синхронной или асинхронной?",
    [A("synchronous_standby_names", True),
     A("synchronous_commit", False),
     A("hot_standby", False),
     A("max_wal_senders", False)]))

Qs.append(Q("Какой параметр master-сервера ограничивает количество одновременных wal_sender?",
    [A("max_wal_senders", True),
     A("max_connections", False),
     A("wal_senders", False),
     A("wal_sender_limit", False)]))

Qs.append(Q("Что такое standby.signal?",
    [A("Файл, указывающий серверу работать в режиме постоянного восстановления (реплики)", True),
     A("Файл конфигурации реплики", False),
     A("Файл с настройками подключения к мастеру", False),
     A("Файл для отключения hot standby", False)]))

# ========== Topic 16: Логическая репликация ==========
Qs.append(Q("Какие команды реплицируются при логической репликации?",
    [A("INSERT", True), A("UPDATE", True),
     A("DELETE", True), A("TRUNCATE", True),
     A("CREATE TABLE", False), A("ALTER TABLE", False)]))

Qs.append(Q("Какой уровень WAL необходим для логической репликации?",
    [A("logical", True), A("replica", False),
     A("minimal", False), A("archive", False)]))

Qs.append(Q("Что такое replica identity?",
    [A("Способ идентификации строк для операций UPDATE/DELETE при логической репликации", True),
     A("Идентификатор реплики на мастере", False),
     A("Тип репликации для реплик", False),
     A("Имя слота репликации", False)]))

Qs.append(Q("Какие конфликты могут возникнуть при логической репликации?",
    [A("Нарушение уникальности", True),
     A("Отсутствие строки на подписчике", True),
     A("Нарушение NOT NULL", True),
     A("Нарушение FOREIGN KEY", False),
     A("Конфликт кодировок", False)]))

Qs.append(Q("Какая команда создаёт подписку на публикацию?",
    [A("CREATE SUBSCRIPTION ... CONNECTION ... PUBLICATION ...", True),
     A("CREATE REPLICATION ... FROM ...", False),
     A("ATTACH SUBSCRIPTION ... TO ...", False),
     A("GRANT PUBLICATION ... TO ...", False)]))

# ===== Dump JSON =====
dump_json(
    "PostgreSQL — Middle (Best Practices)",
    "Тест Middle: 80 вопросов по лучшим практикам, сертификационным темам и эксплуатации PostgreSQL",
    Qs,
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "json", "General_Middle.json")
)
