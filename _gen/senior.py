"""Senior test generator — 80 questions on PostgreSQL advanced operations and tuning."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import A, Q, QN, dump_json

Qs = []

# ========== Topic 01: Установка и управление ==========
Qs.append(Q("Какой параметр определяет максимальное количество подготовленных транзакций?",
    [A("max_prepared_transactions", True),
     A("max_standby_streams", False),
     A("max_replication_slots", False),
     A("max_worker_processes", False)]))

Qs.append(Q("Какие библиотеки можно включить через shared_preload_libraries?",
    [A("pg_stat_statements", True), A("auto_explain", True),
     A("pg_buffercache", True), A("pgcrypto", False),
     A("uuid-ossp", False)]))

Qs.append(Q("Какой параметр задаёт имя экземпляра (кластера)?",
    [A("cluster_name", True), A("instance_name", False),
     A("pg_cluster", False), A("server_name", False)]))

Qs.append(Q("Какая утилита позволяет связать OID объекта с именем файла?",
    [A("oid2name", True), A("pg_lsclusters", False),
     A("pg_controldata", False), A("pg_whoami", False)]))

Qs.append(Q("Какой параметр задаёт время ожидания перед переключением WAL-сегмента при архивировании?",
    [A("archive_timeout", True), A("wal_timeout", False),
     A("archive_completion", False), A("wal_switch_delay", False)]))

# ========== Topic 02: psql и клиентское ПО ==========
Qs.append(Q("Какие переменные psql управляют обработкой ошибок?",
    [A("ON_ERROR_STOP", True), A("ON_ERROR_ROLLBACK", True),
     A("ERROR", False), A("AUTOCOMMIT", False)]))

Qs.append(Q("Какая команда psql выполняет каждый результат выборки как SQL-запрос?",
    [A("\\gexec", True), A("\\g", False),
     A("\\do", False), A("\\go", False)]))

Qs.append(Q("Какие переменные psql хранят информацию о последней ошибке?",
    [A("LAST_ERROR_MESSAGE", True), A("LAST_ERROR_SQLSTATE", True),
     A("SQLSTATE", True), A("LAST_ERROR", False)]))

Qs.append(Q("Как получить план выполнения запроса без его фактического выполнения?",
    [A("EXPLAIN SELECT ...", True),
     A("\\explain SELECT ...", True),
     A("EXPLAIN ANALYZE SELECT ...", False),
     A("\\explain analyze SELECT ...", False)]))

Qs.append(Q("Какие метакоманды psql позволяют получить информацию об объектах?",
    [A("\\d (описание объекта)", True),
     A("\\dt (список таблиц)", True),
     A("\\di (список индексов)", True),
     A("\\dv (список представлений)", True),
     A("\\df (список функций)", True),
     A("\\dp (привилегии)", True)]))

# ========== Topic 03: Конфигурирование сервера ==========
Qs.append(Q("Какой параметр управляет количеством рабочих процессов autovacuum?",
    [A("autovacuum_max_workers", True),
     A("max_worker_processes", False),
     A("max_parallel_workers", False),
     A("autovacuum_parallel", False)]))

Qs.append(Q("Какой параметр задаёт процент от размера таблицы для запуска VACUUM?",
    [A("autovacuum_vacuum_scale_factor", True),
     A("vacuum_threshold", False),
     A("vacuum_cost_scale", False),
     A("vacuum_percentage", False)]))

Qs.append(Q("Какие параметры влияют на планировщик запросов?",
    [A("effective_cache_size", True), A("work_mem", True),
     A("random_page_cost", True), A("seq_page_cost", True),
     A("shared_buffers", False), A("wal_buffers", False)]))

Qs.append(Q("Какой параметр задаёт размер WAL в памяти?",
    [A("wal_buffers", True), A("wal_memory", False),
     A("wal_shared_mem", False), A("wal_cache_size", False)]))

Qs.append(Q("Какой параметр определяет минимальный размер WAL перед контрольной точкой?",
    [A("min_wal_size", True), A("max_wal_size", False),
     A("wal_min_size", False), A("wal_keep", False)]))

# ========== Topic 04: Общее устройство ==========
Qs.append(Q("Какие процессы PostgreSQL управляют WAL?",
    [A("walwriter", True),
     A("walsender", True),
     A("walreceiver", True),
     A("checkpointer", False),
     A("bgwriter", False)]))

Qs.append(Q("Что такое prepared statement в протоколе PostgreSQL?",
    [A("Заранее разобранный и переписанный запрос с сохранённым деревом разбора", True),
     A("Запрос, записанный в журнал предзаписи", False),
     A("Запрос, выполненный на реплике", False),
     A("Запрос, требующий подтверждения транзакции", False)]))

Qs.append(Q("Какие типы процессов PostgreSQL существуют?",
    [A("Postmaster", True), A("Backend (обслуживающие)", True),
     A("Фоновые (checkpointer, walwriter, autovacuum и др.)", True),
     A("Worker-процессы для параллельных запросов", True),
     A("Client-процессы (клиентские приложения)", False)]))

Qs.append(Q("Что такое портал (portal) в PostgreSQL?",
    [A("Представление курсора на сервере — результат подготовленного запроса", True),
     A("Соединение между клиентом и сервером", False),
     A("Журнал выполнения запроса", False),
     A("Кэш системного каталога", False)]))

Qs.append(Q("Какие свойства ACID в PostgreSQL реализуются без WAL?",
    [A("Атомарность", False), A("Согласованность", False),
     A("Изоляция (через MVCC)", False), A("Долговечность", False),
     A("Ни одно из этих свойств, WAL обязателен для долговечности", True)]))

# ========== Topic 05: Изоляция и MVCC ==========
Qs.append(Q("Какие аномалии возможны при уровне Repeatable Read?",
    [A("Phantom reads", True),
     A("Non-repeatable reads", False),
     A("Dirty reads", False),
     A("Lost updates", False)]))

Qs.append(Q("Какой механизм предотвращает дедлоки в PostgreSQL?",
    [A("Ожидание с обратной отсрочкой (wait with backoff) + детекция дедлоков", True),
     A("Приоритеты транзакций", False),
     A("Фиксированный порядок захвата блокировок", False),
     A("Отключение блокировок при дедлоках", False)]))

Qs.append(Q("Какие типы блокировок строк существуют в PostgreSQL?",
    [A("AccessShareLock", True), A("RowShareLock", True),
     A("RowExclusiveLock", True), A("ExclusiveLock", True),
     A("AccessExclusiveLock", True),
     A("WriteLock", False),
     A("UpdateLock", False)]))

Qs.append(Q("Какой уровень изоляции требует обработки ошибок сериализации?",
    [A("Serializable", True), A("Repeatable Read", False),
     A("Read Committed", False), A("Read Uncommitted", False)]))

Qs.append(Q("Что такое Serializable Isolation Failure?",
    [A("Ошибка, возникающая когда PostgreSQL обнаруживает, что сериализация невозможна", True),
     A("Ошибку блокировки из-за нехватки памяти", False),
     A("Ошибку при записи в WAL", False),
     A("Ошибку при чтении из реплики", False)]))

# ========== Topic 06: Очистка (VACUUM) ==========
Qs.append(Q("Что такое table bloat?",
    [A("Разрастание таблицы из-за накопления мёртвых версий строк, которые не были вычищены", True),
     A("Сжатие таблицы при VACUUM FULL", False),
     A("Увеличение размера таблицы при вставке", False),
     A("Переполнение таблицы при превышении размера файла", False)]))

Qs.append(Q("Какие параметры autovacuum можно задать на уровне таблицы?",
    [A("autovacuum_vacuum_threshold", True),
     A("autovacuum_vacuum_scale_factor", True),
     A("autovacuum_analyze_threshold", True),
     A("autovacuum_vacuum_cost_delay", True),
     A("autovacuum_enabled", True)]))

Qs.append(Q("Что такое vacuum cost delay?",
    [A("Задержка, которую autovacuum делает между операциями для снижения нагрузки на I/O", True),
     A("Время, необходимое для выполнения полной очистки", False),
     A("Время между запусками autovacuum", False),
     A("Задержка перед записью WAL", False)]))

Qs.append(Q("Какие команды перестраивают объекты?",
    [A("VACUUM FULL", True), A("REINDEX", True),
     A("CLUSTER", True), A("REINDEX CONCURRENTLY", True),
     A("VACUUM", False), A("ANALYZE", False)]))

Qs.append(Q("Что делает CLUSTER?",
    [A("Пересортировывает строки таблицы по индексу и перестраивает таблицу физически", True),
     A("Создаёт новый индекс для таблицы", False),
     A("Вычищает мёртвые строки из таблицы", False),
     A("Сжимает данные в TOAST-таблице", False)]))

# ========== Topic 07: Буферный кеш и WAL ==========
Qs.append(Q("Какой параметр задаёт количество конкурентных операций ввода-вывода?",
    [A("effective_io_concurrency", True),
     A("io_concurrency", False),
     A("max_io_threads", False),
     A("io_parallelism", False)]))

Qs.append(Q("Какие из перечисленных параметров влияют на производительность записи?",
    [A("wal_buffers", True), A("synchronous_commit", True),
     A("full_page_writes", True), A("max_wal_size", True),
     A("checkpoint_completion_target", True),
     A("shared_buffers", False)]))

Qs.append(Q("Что делает параметр full_page_writes?",
    [A("Включает запись полных страниц в WAL при их первом изменении после контрольной точки", True),
     A("Записывает полный WAL-файл при каждом запросе", False),
     A("Включает полную блокировку при записи", False),
     A("Отключает запись в WAL", False)]))

Qs.append(Q("Какие из перечисленных параметров влияют на производительность чтения?",
    [A("shared_buffers", True), A("effective_cache_size", True),
     A("work_mem", True), A("random_page_cost", True),
     A("max_wal_size", False), A("wal_buffers", False)]))

Qs.append(Q("Что такое checkpoint_flush_after?",
    [A("Порог в байтах, после которого грязные страницы принудительно сбрасываются через ОС", True),
     A("Максимальное время выполнения контрольной точки", False),
     A("Интервал между контрольными точками", False),
     A("Минимальный размер WAL перед контрольной точкой", False)]))

# ========== Topic 08: Базы данных и схемы ==========
Qs.append(Q("Какие привилегии нужны для создания схемы в базе данных?",
    [A("CREATE на уровне БД", True),
     A("USAGE на схеме public", False),
     A("SELECT на pg_namespace", False),
     A("INSERT на pg_database", False)]))

Qs.append(Q("Что произойдёт при попытке удалить схему, в которой есть объекты?",
    [A("Ошибка — нужно указать CASCADE для удаления объектов", True),
     A("Схема и объекты будут удалены", False),
     A("Объекты останутся в схеме public", False),
     A("Схема перейдёт в режим только для чтения", False)]))

Qs.append(Q("Какие системные представления содержат информацию о схемах?",
    [A("pg_namespace", True), A("information_schema.schemata", True),
     A("\\dn", True), A("pg_schemas", False)]))

Qs.append(Q("Что такое pg_temp_N схема?",
    [A("Временная схема для каждого сеанса, содержащая временные объекты", True),
     A("Схема для системных таблиц", False),
     A("Схема для объектов пользователя по умолчанию", False),
     A("Схема для TOAST-таблиц", False)]))

Qs.append(Q("Какие параметры влияют на поиск объектов по имени?",
    [A("search_path", True),
     A("default_tablespace", False),
     A("search_order", False),
     A("schema_priority", False)]))

# ========== Topic 09: Системный каталог ==========
Qs.append(Q("Какие из этих таблиц находятся в pg_catalog?",
    [A("pg_class", True), A("pg_attribute", True),
     A("pg_type", True), A("pg_proc", True),
     A("pg_database", True), A("sys_objects", False)]))

Qs.append(Q("Какая системная таблица хранит информацию о правах доступа?",
    [A("pg_authid", True), A("pg_roles", True),
     A("pg_hba_file_rules", True), A("pg_policy", True),
     A("pg_user_mapping", False), A("pg_permissions", False)]))

Qs.append(Q("Как узнать, какая таблица использует какое табличное пространство?",
    [A("pg_tables.spcname", True), A("pg_class.reltablespace", True),
     A("\\dt+", True), A("pg_tablespace spcname", False)]))

Qs.append(Q("Какой столбец pg_class указывает OID схемы, которой принадлежит объект?",
    [A("relnamespace", True), A("relowner", False),
     A("relschema", False), A("relpath", False)]))

Qs.append(Q("Какие системные представления хранят информацию о блокировках?",
    [A("pg_locks", True), A("pg_stat_activity", True),
     A("pg_blocking_pids", False), A("pg_lock_status", False)]))

# ========== Topic 10: Табличные пространства ==========
Qs.append(Q("Какие объекты хранятся в pg_global?",
    [A("Общие объекты кластера (pg_database, pg_authid, pg_authrol)", True),
     A("Только файлы WAL", False),
     A("Только временные объекты", False),
     A("TOAST-таблицы", False)]))

Qs.append(Q("Что происходит с данными при удалении табличного пространства?",
    [A("Ошибка, если в нём есть объекты; иначе — удаление", True),
     A("Данные перемещаются в pg_default", False),
     A("Данные удаляются принудительно", False),
     A("Данные архивируются", False)]))

Qs.append(Q("Какая функция возвращает размер табличного пространства?",
    [A("pg_tablespace_size('name')", True),
     A("pg_tablespace('name').size", False),
     A("spc_size('name')", False),
     A("SELECT size FROM pg_tablespace", False)]))

Qs.append(Q("Какие параметры задают табличные пространства для временных объектов?",
    [A("temp_tablespaces", True),
     A("temp_tablespace", False),
     A("pg_default_temp", False),
     A("default_temp_tablespace", False)]))

Qs.append(Q("Какая команда перемещает все объекты пользователя в другое табличное пространство?",
    [A("REASSIGN OWNED BY ... TO ...", True),
     A("ALTER USER ... SET TABLESPACE", True),
     A("ALTER TABLE ALL ... SET TABLESPACE", True),
     A("MOVE ALL IN TABLESPACE", False)]))

# ========== Topic 11: Организация данных (файлы, TOAST) ==========
Qs.append(Q("Какие функции PostgreSQL работают с размером объектов?",
    [A("pg_relation_size()", True),
     A("pg_total_relation_size()", True),
     A("pg_table_size()", True),
     A("pg_indexes_size()", True),
     A("pg_size_pretty()", True),
     A("pg_column_size()", True)]))

Qs.append(Q("Какие слои fork существуют у нежурналируемой (UNLOGGED) таблицы?",
    [A("main", True), A("fsm", True), A("vm", True),
     A("init", True),
     A("toast", False)]))

Qs.append(Q("Что произойдёт с UNLOGGED таблицами при восстановлении после сбоя?",
    [A("Они будут очищены и заполнены пустым слоем init", True),
     A("Они будут восстановлены из WAL", False),
     A("Они будут удалены навсегда", False),
     A("Они перейдут в режим только для чтения", False)]))

Qs.append(Q("Какой параметр определяет стратегию сжатия TOAST по умолчанию?",
    [A("default_toast_compression", True),
     A("toast_compression", False),
     A("default_storage_compression", False),
     A("toast_method", False)]))

Qs.append(Q("Как TOAST обрабатывает значения, которые помещаются в одну страницу?",
    [A("Стандартное хранение (plain) — без сжатия и переноса", True),
     A("Сжатие и перенос в TOAST-таблицу", False),
     A("Хранение inline в основной странице", False),
     A("Авто-сжатие алгоритмом lz4", False)]))

# ========== Topic 12: Мониторинг ==========
Qs.append(Q("Какие расширения обеспечивают дополнительную статистику?",
    [A("pg_stat_statements", True), A("pg_buffercache", True),
     A("pgstattuple", True), A("pg_freespacemap", True),
     A("pg_prewarm", True), A("pg_cron", False)]))

Qs.append(Q("Какая функция сбрасывает статистику для текущей базы данных?",
    [A("pg_stat_reset()", True),
     A("pg_stat_reset_database()", False),
     A("pg_reset_stats()", False),
     A("pg_stat_clear()", False)]))

Qs.append(Q("Как узнать, какие запросы потребляют больше всего ресурсов?",
    [A("pg_stat_statements", True),
     A("pg_stat_activity.query", True),
     A("pg_stat_database.blks_read", True),
     A("pg_stat_all_tables.idx_scan", False)]))

Qs.append(Q("Какие данные хранит pg_buffercache?",
    [A("Содержимое буферного кеша PostgreSQL", True),
     A("Статистику запросов", False),
     A("Список активных подключений", False),
     A("Журнал WAL", False)]))

Qs.append(Q("Что такое pg_stat_progress_vacuum?",
    [A("Представление, показывающее прогресс выполнения VACUUM", True),
     A("Журнал ошибок автоочистки", False),
     A("Статистику обращений к таблицам", False),
     A("Список таблиц, требующих очистки", False)]))

# ========== Topic 13: Управление доступом ==========
Qs.append(Q("Какие команды управления доступом существуют в PostgreSQL?",
    [A("GRANT", True), A("REVOKE", True),
     A("ALTER ROLE", True), A("ALTER DEFAULT PRIVILEGES", True),
     A("CREATE ROLE", True),
     A("AUTHORIZE", False)]))

Qs.append(Q("Что делает ALTER DEFAULT PRIVILEGES?",
    [A("Задаёт привилегии по умолчанию для объектов, которые будут созданы в будущем", True),
     A("Изменяет привилегии для существующих объектов", False),
     A("Сбрасывает все привилегии к значениям по умолчанию", False),
     A("Отключает проверку привилегий", False)]))

Qs.append(Q("Какие системные представления хранят информацию о привилегиях?",
    [A("information_schema.table_privileges", True),
     A("information_schema.role_table_grants", True),
     A("pg_class.relacl", True),
     A("pg_namespace.nspacl", True),
     A("pg_roles.rolpriv", False),
     A("pg_grants", False)]))

Qs.append(Q("Как отозвать все привилегии у роли у таблице?",
    [A("REVOKE ALL ON TABLE t FROM role", True),
     A("REVOKE ALL PRIVILEGES ON TABLE t FROM role", True),
     A("DROP TABLE t", False),
     A("ALTER TABLE t DROP ALL FROM role", False)]))

Qs.append(Q("Какие предопределённые роли позволяют чтение данных?",
    [A("pg_read_all_data", True),
     A("pg_read_all_settings", True),
     A("pg_read_all_stats", True),
     A("pg_read_server_files", True),
     A("pg_monitor", True)]))

# ========== Topic 14: Резервное копирование ==========
Qs.append(Q("Какие параметры WAL-архивирования нужны для PITR?",
    [A("archive_mode = on", True),
     A("archive_command", True),
     A("wal_level = replica", True),
     A("checkpoint_timeout", True),
     A("max_wal_size", False),
     A("shared_buffers", False)]))

Qs.append(Q("Какие утилиты PostgreSQL поддерживают параллельное выполнение?",
    [A("pg_dump --jobs", True),
     A("pg_restore --jobs", True),
     A("pg_basebackup", False),
     A("pg_dumpall", False)]))

Qs.append(Q("Какой формат pg_dump позволяет восстановить только определённые объекты?",
    [A("custom", True), A("directory", True),
     A("plain", False), A("tar", False)]))

Qs.append(Q("Что такое backup_label?",
    [A("Файл, созданный pg_basebackup, содержащий информацию о базовой резервной копии", True),
     A("Файл конфигурации для восстановления", False),
     A("Журнал выполненных резервных копий", False),
     A("Файл с параметрами резервной копии", False)]))

Qs.append(Q("Какой файл указывает PostgreSQL на необходимость восстановления?",
    [A("recovery.signal (или standby.signal для реплики)", True),
     A("restore.signal", False),
     A("backup.signal", False),
     A("pg_restore.signal", False)]))

# ========== Topic 15: Физическая репликация ==========
Qs.append(Q("Какие параметры настройки физической репликации?",
    [A("primary_conninfo", True), A("primary_slot_name", True),
     A("hot_standby = on", True), A("synchronous_standby_names", True),
     A("synchronous_commit", True),
     A("replica_mode", False)]))

Qs.append(Q("Какой параметр определяет режим синхронной репликации?",
    [A("synchronous_commit", True),
     A("synchronous_standby_names", True),
     A("synchronous_mode", False),
     A("sync_replication", False)]))

Qs.append(Q("Какие режимы синхронной репликации существуют?",
    [A("on (гарантированная)", True),
     A("remote_apply (реплики применили на standby)", True),
     A("remote_write (записано на standby)", True),
     A("local (записано на master)", True),
     A("async", True),
     A("fast", False)]))

Qs.append(Q("Какие представления показывают состояние репликации?",
    [A("pg_stat_replication (на мастере)", True),
     A("pg_stat_wal_receiver (на реплике)", True),
     A("pg_replication_slots", True),
     A("pg_stat_all_tables", False)]))

Qs.append(Q("Что такое replication slot?",
    [A("Серверный объект, удерживающий WAL-файлы до их прочтения клиентом", True),
     A("Клиентский параметр подключения", False),
     A("Список реплик в кластере", False),
     A("Параметр синхронной репликации", False)]))

# ========== Topic 16: Логическая репликация ==========
Qs.append(Q("Какие объекты создаются при логической репликации?",
    [A("Publication", True), A("Subscription", True),
     A("Replication slot", True),
     A("Materialized view", False),
     A("Foreign table", False)]))

Qs.append(Q("Какая команда показывает информацию о публикации?",
    [A("\\dRp+", True),
     A("\\dp+", False),
     A("\\dR+", False),
     A("\\dRp", True)]))

Qs.append(Q("Какие ограничения есть у логической репликации?",
    [A("DDL не реплицируется", True),
     A("Таблица должна иметь PRIMARY KEY или UNIQUE NOT NULL", True),
     A("Не реплицируются TRUNCATE по умолчанию (нужно указать)", True),
     A("Только одна публикация на подписку", False),
     A("Требует одинаковых версий PostgreSQL", False)]))

Qs.append(Q("Какой тип репликации позволяет реплицировать только часть строк?",
    [A("Логическая репликация с фильтром (FOR TABLE ... WHERE ...)", True),
     A("Физическая репликация с фильтром", False),
     A("Репликация по схеме", False),
     A("Репликация с pglogical", False)]))

Qs.append(Q("Какие параметры подписки (subscription) можно настроить?",
    [A("create_subscription", True),
     A("binary", False),
     A("streaming", True),
     A("two_phase", True),
     A("enabled", True),
     A("copy_data", True)]))

# ===== Dump JSON =====
dump_json(
    "PostgreSQL — Senior (Advanced Operations)",
    "Тест Senior: 80 вопросов по продвинутой эксплуатации, настройке и HA PostgreSQL",
    Qs,
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "json", "General_Senior.json")
)
