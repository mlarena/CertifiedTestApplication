"""Master test generator — 80 expert-level PostgreSQL questions."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import A, Q, QN, dump_json

Qs = []

# ========== Topic 01: Установка и управление ==========
Qs.append(Q("Какой параметр сборки (--with-...) позволяет изменить размер сегмента файла?",
    [A("--with-segsize", True), A("--with-blocksize", False),
     A("--with-segment-size", False), A("--with-file-size", False)]))

Qs.append(Q("Какая система сборки появилась в PostgreSQL 16 как альтернатива GNU Make?",
    [A("Meson", True), A("CMake", False), A("Ninja", False), A("Bazel", False)]))

Qs.append(Q("Какие библиотеки используются для сжатия в PostgreSQL?",
    [A("zlib", True), A("lz4", True), A("zstd", True),
     A("brotli", False), A("snappy", False)]))

Qs.append(Q("Какой параметр --with-... включает поддержку JIT-компиляции?",
    [A("--with-llvm", True), A("--with-jit", False),
     A("--with-llvmjit", True), A("--with-gcc", False)]))

Qs.append(Q("Какой параметр --with-... задаёт порт по умолчанию при сборке?",
    [A("--with-pgport", True), A("--with-port", False),
     A("--with-default-port", False), A("--with-tcp-port", False)]))

# ========== Topic 02: psql и клиентское ПО ==========
Qs.append(Q("Какая переменная psql управляет количеством строк, извлекаемых за раз?",
    [A("FETCH_COUNT", True), A("PAGER", False),
     A("ROWS", False), A("BATCH_SIZE", False)]))

Qs.append(Q("Какие переменные psql используются для условных конструкций в скриптах?",
    [A("\\if", True), A("\\else", True),
     A("\\endif", True), A("\\{?variable}", True),
     A("\\case", False), A("\\when", False)]))

Qs.append(Q("Как записать результат запроса в переменную psql?",
    [A("\\gset", True), A("\\set var SELECT ...", False),
     A("\\store SELECT ... INTO var", False),
     A("SELECT ... \\to var", False)]))

Qs.append(Q("Какие переменные psql хранят информацию о подключении?",
    [A("DBNAME", True), A("USER", True),
     A("HOST", True), A("PORT", True),
     A("SERVER_VERSION_NAME", True),
     A("PGDATA", False)]))

Qs.append(Q("Какие скрипты выполняются при запуске psql?",
    [A("Системный psqlrc", True), A("~/.psqlrc", True),
     A("~/.psql_history", False), A("/etc/profile", False)]))

# ========== Topic 03: Конфигурирование сервера ==========
Qs.append(Q("Какой параметр влияет на планирование параллельных запросов?",
    [A("max_parallel_workers_per_gather", True),
     A("max_parallel_workers", True),
     A("min_parallel_table_scan_size", True),
     A("parallel_setup_cost", True),
     A("shared_buffers", False)]))

Qs.append(Q("Какие параметры влияют на производительность сортировок?",
    [A("work_mem", True), A("maintenance_work_mem", True),
     A("effective_cache_size", False), A("shared_buffers", False)]))

Qs.append(Q("Что такое huge_pages в контексте PostgreSQL?",
    [A("Использование больших страниц памяти ОС для буферного кеша", True),
     A("Увеличение размера страницы данных", False),
     A("Разделение буферного кеша на сегменты", False),
     A("Управление размером WAL-файлов", False)]))

Qs.append(Q("Какой параметр определяет максимальный объём временных файлов на сеанс?",
    [A("temp_file_limit", True),
     A("temp_tablespace_limit", False),
     A("work_mem", False),
     A("max_temp_files", False)]))

Qs.append(Q("Какой параметр контролирует, какой размер таблицы считается «маленькой» для планировщика?",
    [A("effective_cache_size", False),
     A("min_parallel_table_scan_size", True),
     A("small_table_threshold", False),
     A("table_size_threshold", False)]))

# ========== Topic 04: Общее устройство ==========
Qs.append(Q("Какие этапы выполнения запроса существуют в PostgreSQL?",
    [A("Разбор (parser)", True),
     A("Переписывание (rewriter)", True),
     A("Планирование (planner)", True),
     A("Выполнение (executor)", True),
     A("Оптимизация (optimizer)", False),
     A("Трансляция (translator)", False)]))

Qs.append(Q("Что такое JIT-компиляция в PostgreSQL?",
    [A("Компиляция выражений запроса в машинный код через LLVM для ускорения вычислений", True),
     A("Кеширование результатов запросов", False),
     A("Предварительная компиляция хранимых процедур", False),
     A("Динамическая загрузка расширений", False)]))

Qs.append(Q("Какие механизмы PostgreSQL поддерживают расширяемость?",
    [A("Расширения (extensions)", True),
     A("Языки программирования (PL/Perl, PL/Python)", True),
     A("Foreign Data Wrappers", True),
     A("Пользовательские типы данных", True),
     A("Пользовательские индексы", True)]))

Qs.append(Q("Что такое FDW (Foreign Data Wrapper)?",
    [A("Механизм подключения к внешним источникам данных через интерфейс PostgreSQL", True),
     A("Фоновый рабочий процесс для распределённых вычислений", False),
     A("Формат данных для экспорта", False),
     A("Протокол передачи WAL", False)]))

Qs.append(Q("Какие процессы PostgreSQL являются фоновыми?",
    [A("checkpointer", True), A("background writer", True),
     A("walwriter", True), A("autovacuum launcher", True),
     A("logical replication launcher", True),
     A("walsender", False)]))

# ========== Topic 05: Изоляция и MVCC ==========
Qs.append(Q("Что такое snapshot isolation?",
    [A("Изоляция, при которой транзакция видит согласованный срез данных на момент начала", True),
     A("Изоляция, при которой транзакция блокирует все таблицы", False),
     A("Изоляция через сериализацию запросов", False),
     A("Изоляция через журнал предзаписи", False)]))

Qs.append(Q("Какие проблемы решает Serializable Snapshot Isolation (SSI)?",
    [A("Write skew", True), A("Read skew", True),
     A("Phantom reads", True),
     A("Dirty reads", False),
     A("Lost updates", False)]))

Qs.append(Q("Что такое predicate lock в PostgreSQL?",
    [A("Блокировка, основанная на предикатах запроса, для обеспечения Serializable изоляции", True),
     A("Блокировка строк по предикату WHERE", False),
     A("Блокировка таблицы для секции", False),
     A("Блокировка при проверке ограничений", False)]))

Qs.append(Q("Какие свойства гарантируются уровнем Read Committed?",
    [A("Нет грязных чтений", True),
     A("Нет потерянных обновлений", True),
     A("Нет non-repeatable reads в одном операторе", True),
     A("Нет phantom reads", False),
     A("Полная изоляция", False)]))

Qs.append(Q("Что такое «hot snapshot» в PostgreSQL?",
    [A("Снимок данных, который может строиться на реплике без блокировок", False),
     A("Снимок, используемый при VACUUM FULL", False),
     A("Снимок, который не имеет отношения к PostgreSQL", True),
     A("Снимок, используемый для восстановления", False)]))

# ========== Topic 06: Очистка (VACUUM) ==========
Qs.append(Q("Какой параметр задаёт максимальный возраст unfrozen транзакции?",
    [A("autovacuum_freeze_max_age", True),
     A("vacuum_freeze_table_age", True),
     A("vacuum_multixact_freeze_min_age", False),
     A("max_transaction_age", False)]))

Qs.append(Q("Что происходит, если счетчик транзакций переполнится?",
    [A("Сервер аварийно остановится и потребует ручной заморозки", True),
     A("Номера транзакций будут сброшены автоматически", False),
     A("Сервер продолжит работу, но производительность упадёт", False),
     A("Будет создан новый кластер", False)]))

Qs.append(Q("Какие команды влияют на заморозку страниц?",
    [A("VACUUM", True), A("VACUUM FULL", True),
     A("CREATE INDEX CONCURRENTLY", False),
     A("REINDEX", False),
     A("CLUSTER", True)]))

Qs.append(Q("Что такое vacuum_freeze_min_age?",
    [A("Минимальный возраст версии строки (в транзакциях), при котором она может быть заморожена", True),
     A("Максимальный возраст таблицы перед полной очисткой", False),
     A("Время между запусками VACUUM", False),
     A("Возраст строки, после которого она удаляется", False)]))

Qs.append(Q("Какой параметр управляет интенсивностью autovacuum?",
    [A("autovacuum_vacuum_cost_limit", True),
     A("autovacuum_vacuum_cost_delay", True),
     A("vacuum_cost_limit", True),
     A("vacuum_cost_delay", True),
     A("autovacuum_intensity", False)]))

# ========== Topic 07: Буферный кеш и WAL ==========
Qs.append(Q("Какие параметры влияют на частоту контрольных точек?",
    [A("checkpoint_timeout", True), A("max_wal_size", True),
     A("checkpoint_completion_target", True),
     A("wal_writer_delay", False),
     A("full_page_writes", False)]))

Qs.append(Q("Что такое WAL-сегмент?",
    [A("Физический файл журнала фиксированного размера (обычно 16 МБ)", True),
     A("Логическая единица журнальной записи", False),
     A("Буфер WAL в памяти", False),
     A("Участок WAL для одной транзакции", False)]))

Qs.append(Q("Какие функции PostgreSQL работают с WAL?",
    [A("pg_current_wal_lsn()", True),
     A("pg_switch_wal()", True),
     A("pg_walfile_name()", True),
     A("pg_create_restore_point()", True),
     A("pg_wal_replay()", False)]))

Qs.append(Q("Какие расширения позволяют анализировать содержимое WAL?",
    [A("pg_waldump", True), A("test_decoding", True),
     A("pg_logical", False),
     A("wal2json", True),
     A("pg_wal_analyzer", False)]))

Qs.append(Q("Какой параметр определяет, сколько записей WAL буферизуется в памяти?",
    [A("wal_buffers", True),
     A("wal_writer_delay", False),
     A("max_wal_size", False),
     A("shared_buffers", False)]))

# ========== Topic 08: Базы данных и схемы ==========
Qs.append(Q("Какие ограничения накладывает использование разных табличных пространств?",
    [A("Объекты в разных ТП не могут иметь общих индексов", False),
     A("Табличные пространства не могут разделяться между кластерами", True),
     A("Временные таблицы не могут использовать temp_tablespaces", False),
     A("Табличные пространства не могут быть на разных дисках", False)]))

Qs.append(Q("Что такое pg_database_owner?",
    [A("Псевдороль, представляющая владельца текущей базы данных", True),
     A("Реальная роль, созданная при инициализации", False),
     A("Роль, которая всегда является владельцем public схемы", False),
     A("Пользователь postgres", False)]))

Qs.append(Q("Какие объекты нельзя переместить между схемами?",
    [A("Индексы (перемещаются вместе с таблицей)", True),
     A("Функции с зависимостями", False),
     A("Типы данных с зависимостями", False),
     A("Роли", True),
     A("Табличные пространства", True)]))

Qs.append(Q("Какая команда пересоздаёт все представления, зависимые от изменённой таблицы?",
    [A("ALTER TABLE ... CASCADE (неверно)", False),
     A("DROP VIEW + CREATE VIEW (вручную)", True),
     A("ALTER VIEW ... RECREATE", False),
     A("pg_dump + pg_restore", False)]))

Qs.append(Q("Какие объекты создаются при выполнении CREATE DATABASE?",
    [A("Записи в pg_database", True),
     A("Каталог в PGDATA/base/", True),
     A("Схема pg_catalog", True),
     A("Схема public", True),
     A("Схема pg_toast", False),
     A("Файлы WAL", False)]))

# ========== Topic 09: Системный каталог ==========
Qs.append(Q("Какие представления системного каталога содержат информацию о зависимостях?",
    [A("pg_depend", True), A("pg_class", True),
     A("pg_rewrite", True), A("pg_attrdef", True),
     A("pg_inherits", True),
     A("pg_deps", False)]))

Qs.append(Q("Как узнать, от каких объектов зависит представление?",
    [A("Запрос к pg_depend", True),
     A("Команда \\d+ view_name", True),
     A("pg_dump --schema", True),
     A("SELECT * FROM pg_views", False)]))

Qs.append(Q("Какие таблицы системного каталога являются общими для кластера?",
    [A("pg_database", True), A("pg_authid", True),
     A("pg_tablespace", True), A("pg_db_role_setting", True),
     A("pg_class", False), A("pg_attribute", False)]))

Qs.append(Q("Какие представления предоставляют стандарт SQL?",
    [A("information_schema.tables", True),
     A("information_schema.columns", True),
     A("information_schema.routines", True),
     A("information_schema.privileges", True),
     A("pg_class", False)]))

Qs.append(Q("Какой OID у схемы pg_catalog?",
    [A("11", True), A("2200", False),
     A("0", False), A("Зависит от кластера", False)]))

# ========== Topic 10: Табличные пространства ==========
Qs.append(Q("Какие операции блокируют доступ к таблице при перемещении между ТП?",
    [A("ALTER TABLE SET TABLESPACE блокирует доступ полностью", True),
     A("Перемещение происходит онлайн без блокировок", False),
     A("Блокируется только запись", False),
     A("Блокируется только чтение", False)]))

Qs.append(Q("Как переместить все индексы таблицы в другое табличное пространство?",
    [A("REINDEX (TABLESPACE ts) TABLE t", True),
     A("ALTER INDEX ... SET TABLESPACE (для каждого)", True),
     A("ALTER TABLE ... SET TABLESPACE", False),
     A("MOVE INDEXES TO TABLESPACE", False)]))

Qs.append(Q("Какие объекты нельзя разместить в пользовательском табличном пространстве?",
    [A("Объекты системного каталога кластера (pg_global)", True),
     A("Временные таблицы", False),
     A("Файлы WAL", True),
     A("Индексы", False)]))

Qs.append(Q("Как узнать размер всех объектов в табличном пространстве?",
    [A("pg_tablespace_size('ts')", True),
     A("\\db+", True),
     A("SELECT * FROM pg_tablespace WHERE spcname='ts'", False),
     A("du -sh /path/to/ts", True)]))

Qs.append(Q("Какие особенности у temp_tablespaces?",
    [A("Можно указать несколько ТП", True),
     A("Сервер выбирает одно из них случайным образом", True),
     A("Используется только для временных таблиц", True),
     A("Обязательно должно существовать при запуске сервера", False)]))

# ========== Topic 11: Организация данных ==========
Qs.append(Q("Какие операторы работают с TOAST?",
    [A("pg_column_size()", True),
     A("pg_compression()", False),
     A("pg_detoast_datum()", True),
     A("toast_compress()", False)]))

Qs.append(Q("Какие параметры pgstattuple позволяют оценить разрастание?",
    [A("pgstattuple()", True), A("pgstattuple_approx()", True),
     A("pgstatindex()", True),
     A("pg_bloat_ratio()", False),
     A("pg_dead_tuples()", False)]))

Qs.append(Q("Какие функции возвращают информацию о файлах?",
    [A("pg_relation_filepath()", True),
     A("pg_ls_dir()", True),
     A("pg_stat_file()", True),
     A("pg_ls_waldir()", True),
     A("pg_file_list()", False)]))

Qs.append(Q("Что такое relfilenode?",
    [A("Числовой идентификатор файла объекта на диске", True),
     A("Имя файла в системе", False),
     A("OID таблицы", False),
     A("Номер сегмента файла", False)]))

Qs.append(Q("Какие изменения структуры таблицы приводят к перестроению (rewrite)?",
    [A("ALTER COLUMN TYPE", True),
     A("ADD COLUMN с DEFAULT (в старых версиях)", True),
     A("DROP COLUMN", False),
     A("RENAME COLUMN", False),
     A("SET NOT NULL", False)]))

# ========== Topic 12: Мониторинг ==========
Qs.append(Q("Какие представления содержат информацию о блокировках?",
    [A("pg_locks", True), A("pg_stat_activity", True),
     A("pg_blocking_pids()", True),
     A("pg_stat_progress_cluster", False)]))

Qs.append(Q("Какие параметры влияют на сбор статистики pg_stat_statements?",
    [A("pg_stat_statements.max", True),
     A("pg_stat_statements.track", True),
     A("pg_stat_statements.track_utility", True),
     A("shared_preload_libraries", True)]))

Qs.append(Q("Какие функции управляют статистикой?",
    [A("pg_stat_reset()", True),
     A("pg_stat_reset_shared()", True),
     A("pg_stat_reset_single_table_counters()", True),
     A("pg_stat_clear_snapshot()", True),
     A("pg_stat_flush()", False)]))

Qs.append(Q("Какие столбцы pg_stat_activity полезны для диагностики?",
    [A("query", True), A("state", True),
     A("wait_event_type", True), A("wait_event", True),
     A("pg_blocking_pids()", True),
     A("query_cost", False)]))

Qs.append(Q("Какие представления показывают прогресс выполнения команд?",
    [A("pg_stat_progress_analyze", True),
     A("pg_stat_progress_vacuum", True),
     A("pg_stat_progress_create_index", True),
     A("pg_stat_progress_basebackup", True),
     A("pg_stat_progress_copy", True),
     A("pg_stat_progress_query", False)]))

# ========== Topic 13: Управление доступом ==========
Qs.append(Q("Какие типы политик RLS (Row Level Security) существуют?",
    [A("PERMISSIVE", True), A("RESTRICTIVE", True),
     A("DEFAULT", False), A("EXCLUSIVE", False)]))

Qs.append(Q("Что такое SECURITY LABEL в PostgreSQL?",
    [A("Метка безопасности для объектов, используемая расширениями (SELinux, sepgsql)", True),
     A("Шифрование данных таблицы", False),
     A("Установка пароля для роли", False),
     A("Маркировка транзакций", False)]))

Qs.append(Q("Какие привилегии доступны для функций?",
    [A("EXECUTE", True),
     A("SELECT", False),
     A("INSERT", False),
     A("ALTER", False)]))

Qs.append(Q("Что такое proxy user?",
    [A("Роль, от имени которой приложение выполняет действия без явного подключения", False),
     A("pg_hba.conf rule для прокси-сервера", False),
     A("Механизм, не поддерживаемый PostgreSQL", True),
     A("pg_ident.conf mapping", True)]))

Qs.append(Q("Какие команды связаны с управлением ролями?",
    [A("CREATE ROLE", True), A("ALTER ROLE", True),
     A("DROP ROLE", True), A("GRANT", True),
     A("REVOKE", True), A("SET ROLE", True)]))

# ========== Topic 14: Резервное копирование ==========
Qs.append(Q("Какие параметры pg_basebackup существуют?",
    [A("--format=tar|plain", True),
     A("--wal-method=stream|fetch|none", True),
     A("--checkpoint=fast|spread", True),
     A("--compression=gzip|lz4|zstd", True),
     A("--label", True),
     A("--incremental", False)]))

Qs.append(Q("Какие инструменты поддерживают инкрементное резервное копирование?",
    [A("pgBackRest", True), A("Barman", True),
     A("WAL-G", True),
     A("pg_basebackup", False),
     A("pg_dump", False)]))

Qs.append(Q("Какие параметры восстановления (recovery_target) существуют?",
    [A("recovery_target_time", True),
     A("recovery_target_xid", True),
     A("recovery_target_lsn", True),
     A("recovery_target_name", True),
     A("recovery_target_action", True)]))

Qs.append(Q("Что такое recovery.signal?",
    [A("Файл в PGDATA, указывающий серверу войти в режим восстановления при запуске", True),
     A("Файл, создаваемый pg_basebackup", False),
     A("Файл конфигурации WAL-архива", False),
     A("Файл с параметрами репликации", False)]))

Qs.append(Q("Какие команды pg_dump позволяют выбрать объекты?",
    [A("--table", True), A("--schema", True),
     A("--exclude-table", True),
     A("--data-only", True),
     A("--schema-only", True),
     A("--where", False)]))

# ========== Topic 15: Физическая репликация ==========
Qs.append(Q("Какие параметры репликации влияют на задержку?",
    [A("synchronous_commit", True),
     A("wal_sender_timeout", True),
     A("wal_receiver_timeout", True),
     A("max_wal_senders", True),
     A("checkpoint_timeout", False)]))

Qs.append(Q("Какие утилиты обеспечивают автоматический failover?",
    [A("Patroni", True), A("repmgr", True),
     A("pg_auto_failover", True),
     A("pg_basebackup", False),
     A("pg_ctl", False)]))

Qs.append(Q("Какие инструменты балансировки нагрузки для реплик?",
    [A("Pgpool-II", True), A("HAProxy + repmgr", True),
     A("pgBouncer (connection pool)", True),
     A("pg_dump", False)]))

Qs.append(Q("Что такое logical decoding?",
    [A("Извлечение изменений из WAL в логическом формате для подписчиков", True),
     A("Шифрование WAL перед записью", False),
     A("Сжатие WAL для архива", False),
     A("Процесс проверки контрольных сумм", False)]))

Qs.append(Q("Какие расширения для репликации существуют?",
    [A("pglogical", True), A("slony1", True),
     A("pg_repack", False),
     A("pg_partman", False)]))

# ========== Topic 16: Логическая репликация ==========
Qs.append(Q("Какие расширения для логического декодирования существуют?",
    [A("test_decoding", True), A("wal2json", True),
     A("pglogical", True),
     A("pgoutput", True),
     A("pg_decode", False)]))

Qs.append(Q("Какие особенности репликации последовательностей (sequences)?",
    [A("Последовательности не реплицируются логической репликацией", True),
     A("Последовательности реплицируются автоматически", False),
     A("Последовательности реплицируются как таблицы", False),
     A("Последовательности реплицируются физической репликацией", True)]))

Qs.append(Q("Какие параметры подписки влияют на начальную синхронизацию?",
    [A("copy_data", True),
     A("create_slot", True),
     A("two_phase", True),
     A("streaming", True),
     A("connect_timeout", False)]))

Qs.append(Q("Как отследить задержку логической репликации?",
    [A("pg_stat_subscription", True),
     A("pg_replication_slots", True),
     A("pg_wal_lsn_diff()", True),
     A("pg_current_wal_lsn()", True),
     A("pg_stat_replication", False)]))

Qs.append(Q("Какие таблицы не могут быть опубликованы?",
    [A("Таблицы без PRIMARY KEY или REPLICA IDENTITY", True),
     A("Таблицы системного каталога", True),
     A("Временные таблицы", True),
     A("Таблицы с TOAST", False)]))

# ===== Dump JSON =====
dump_json(
    "PostgreSQL — Master (Expert)",
    "Тест Master: 80 экспертных вопросов по внутреннему устройству, настройке, репликации и администрированию PostgreSQL",
    Qs,
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "json", "General_Master.json")
)
