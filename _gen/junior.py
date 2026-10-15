"""Junior test generator — 80 questions based strictly on DBA1 lectures."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import A, Q, QN, dump_json

Qs = []

# ========== Topic 01: Установка и управление сервером ==========
Qs.append(Q("Можно ли запускать инициализацию кластера (initdb) от имени суперпользователя операционной системы (root)?",
    [A("Нет, каталог кластера не может принадлежать суперпользователю ОС", True),
     A("Да, если указан ключ --allow-root", False),
     A("Да, но только для тестовых баз данных", False),
     A("Да, если переменная PGDATA установлена", False)]))

Qs.append(Q("Какой ключ initdb включает подсчёт контрольных сумм страниц данных?",
    [A("-k (или --data-checksums)", True),
     A("--wal-checksums", False),
     A("-A", False),
     A("--page-crc", False)]))

Qs.append(Q("Какие режимы останова поддерживает утилита pg_ctl stop?",
    [A("smart", True), A("fast", True), A("immediate", True),
     A("graceful", False), A("crash", False), A("forced", False)]))

Qs.append(Q("Что делает команда pg_ctl reload?",
    [A("Перечитывает конфигурационные файлы без перезапуска сервера", True),
     A("Выполняет контрольную точку и перезапускает сервер", False),
     A("Останавливает все подключения и очищает буферный кеш", False),
     A("Перезапускает сервер в режиме восстановления", False)]))

# ========== Topic 02: Использование psql ==========
Qs.append(Q("Какая команда psql показывает информацию о текущем подключении?",
    [A("\\conninfo", True),
     A("\\status", False),
     A("\\connection", False),
     A("\\conn", False)]))

Qs.append(Q("Как получить справку по синтаксису SQL-команды в psql?",
    [A("\\help команда (или \\h команда)", True),
     A("man команда", False),
     A("\\? команда", False),
     A("help команда", False)]))

Qs.append(Q("Какая команда psql позволяет записать вывод запроса в файл?",
    [A("\\o [имя_файла]", True),
     A("\\f [имя_файла]", False),
     A("\\copy TO [имя_файла]", False),
     A("\\write [имя_файла]", False)]))

Qs.append(Q("Какие из перечисленных команд psql влияют на формат вывода результатов запросов?",
    [A("\\a (выравнивание)", True),
     A("\\t (только строки, без заголовков)", True),
     A("\\x (расширенный формат)", True),
     A("\\format (альтернативное форматирование)", False),
     A("\\output (вывод в файл)", False),
     A("\\align (выравнивание колонок)", False)]))

Qs.append(Q("Чем команда SQL COPY ... TO 'файл' отличается от psql-команды \\copy ... TO 'файл'?",
    [A("COPY работает с файлами на сервере от имени пользователя postgres, \\copy — с файлами на стороне клиента", True),
     A("COPY работает медленнее, чем \\copy", False),
     A("COPY поддерживает только формат CSV, \\copy — только текстовый", False),
     A("COPY автоматически создает таблицу, если она не существует", False)]))

Qs.append(Q("Какая команда psql выполняет содержимое файла как скрипт?",
    [A("\i [имя_файла] (или \include)", True),
     A("\run [имя_файла]", False),
     A("\exec [имя_файла]", False),
     A("\source [имя_файла]", False)]))

# ========== Topic 03: Конфигурирование сервера ==========
Qs.append(Q("Какой параметр PostgreSQL задаёт размер буферного кеша и требует перезапуска сервера для изменения?",
    [A("shared_buffers", True),
     A("effective_cache_size", False),
     A("work_mem", False),
     A("maintenance_work_mem", False)]))

Qs.append(Q("Какой SQL-интерфейс используется для изменения параметров в файле postgresql.auto.conf?",
    [A("ALTER SYSTEM SET", True),
     A("SET GLOBAL параметр", False),
     A("ALTER CONFIGURATION SET", False),
     A("UPDATE pg_settings SET", False)]))

Qs.append(Q("Какие параметры можно изменить без перезапуска сервера?",
    [A("shared_preload_libraries", False),
     A("shared_buffers", False),
     A("work_mem", True),
     A("max_connections", False),
     A("log_statement", True),
     A("data_directory", False)]))

Qs.append(Q("Что делает параметр track_counts?",
    [A("Включает сбор статистики обращений к таблицам и индексам", True),
     A("Отслеживает количество подключений пользователей", False),
     A("Включает запись всех SQL-команд в журнал", False),
     A("Собирает статистику по операциям ввода-вывода", False)]))

Qs.append(Q("Какой параметр управляет списком библиотек, загружаемых при старте сервера?",
    [A("shared_preload_libraries", True),
     A("preload_libraries", False),
     A("shared_libraries", False),
     A("init_libraries", False)]))

# ========== Topic 04: Общее устройство PostgreSQL ==========
Qs.append(Q("Какое свойство транзакции ACID означает, что транзакция выполняется полностью или не выполняется вовсе?",
    [A("Атомарность", True),
     A("Согласованность", False),
     A("Изоляция", False),
     A("Долговечность", False)]))

Qs.append(Q("Какой процесс PostgreSQL при старте запускает все остальные процессы и следит за ними?",
    [A("postmaster", True),
     A("backend", False),
     A("walwriter", False),
     A("checkpointer", False)]))

Qs.append(Q("Для чего используется пул соединений (например, pgBouncer)?",
    [A("Для уменьшения количества обслуживающих процессов при большом числе клиентов", True),
     A("Для распределения нагрузки между несколькими серверами PostgreSQL", False),
     A("Для автоматического создания резервных копий", False),
     A("Для кэширования результатов SQL-запросов", False)]))

Qs.append(Q("Какой размер страницы данных используется в PostgreSQL по умолчанию?",
    [A("8 Кбайт", True),
     A("4 Кбайта", False),
     A("16 Кбайт", False),
     A("32 Кбайта", False)]))

Qs.append(Q("Какие из перечисленных типов индексов поддерживаются в PostgreSQL по умолчанию (без расширений)?",
    [A("B-деревья", True),
     A("Hash-индексы", True),
     A("GiST", True),
     A("GIN", True),
     A("SP-GiST", True),
     A("BRIN", True),
     A("R-деревья", False)]))

# ========== Topic 05: Изоляция и многоверсионность (MVCC) ==========
Qs.append(Q("Какой уровень изоляции используется в PostgreSQL по умолчанию?",
    [A("Read Committed", True),
     A("Read Uncommitted", False),
     A("Repeatable Read", False),
     A("Serializable", False)]))

Qs.append(Q("Как PostgreSQL обеспечивает изоляцию транзакций без блокировок для читающих транзакций?",
    [A("Через многоверсионность (MVCC) — каждая транзакция видит свою версию данных", True),
     A("Через блокировку всех таблиц на чтение", False),
     A("Через копирование таблиц для каждой транзакции", False),
     A("Через запись данных в память, а не на диск", False)]))

Qs.append(Q("Что такое снимок данных (snapshot) в PostgreSQL?",
    [A("Согласованный срез данных на определённый момент времени", True),
     A("Физическая копия таблицы на диске", False),
     A("Журнал всех изменений в таблице", False),
     A("Индекс, ускоряющий поиск по дате", False)]))

Qs.append(Q("Какая скрытая колонка таблицы показывает номер транзакции, создавшей версию строки?",
    [A("xmin", True),
     A("xmax", False),
     A("xact", False),
     A("xid", False)]))

Qs.append(Q("Какая скрытая колонка показывает номер транзакции, удалившей версию строки (0 — строка актуальна)?",
    [A("xmax", True),
     A("xmin", False),
     A("xdel", False),
     A("xend", False)]))

# ========== Topic 06: Очистка (VACUUM) ==========
Qs.append(Q("Какой фоновый процесс в PostgreSQL автоматически выполняет очистку таблиц?",
    [A("Autovacuum launcher и autovacuum worker", True),
     A("checkpointer", False),
     A("walwriter", False),
     A("bgwriter", False)]))

Qs.append(Q("Что делает команда VACUUM в PostgreSQL?",
    [A("Вычищает мёртвые версии строк из таблиц и обновляет статистику", True),
     A("Удаляет все данные из таблицы и освобождает место на диске", False),
     A("Сжимает данные таблицы и перестраивает индексы", False),
     A("Архивирует данные в отдельный файл", False)]))

Qs.append(Q("Что такое VACUUM FULL?",
    [A("Полная очистка, перестраивающая таблицу и освобождающая место на диске, но полностью блокирующая доступ к таблице", True),
     A("Ускоренная версия обычного VACUUM, не блокирующая таблицу", False),
     A("Команда для очистки только индексов", False),
     A("Аналог команды TRUNCATE", False)]))

Qs.append(Q("Что такое REINDEX ... CONCURRENTLY?",
    [A("Перестроение индексов без блокировки таблицы на запись, но с риском неудачи из-за взаимоблокировок", True),
     A("Полная блокировка таблицы на время перестроения", False),
     A("Команда, которая не работает в транзакциях и не применяется к системным индексам", True),
     A("Автоматическое перестроение индексов по расписанию", False)]))

Qs.append(Q("Какой параметр позволяет отключить автоматическую очистку для конкретной таблицы?",
    [A("WITH (autovacuum_enabled = off)", True),
     A("SET autovacuum = off", False),
     A("ALTER TABLE ... DISABLE VACUUM", False),
     A("CREATE TABLE ... NO VACUUM", False)]))

# ========== Topic 07: Буферный кеш и WAL ==========
Qs.append(Q("Какой алгоритм вытеснения страниц используется в буферном кеше PostgreSQL?",
    [A("LRU (Least Recently Used)", True),
     A("FIFO (First In, First Out)", False),
     A("LFU (Least Frequently Used)", False),
     A("Random replacement", False)]))

Qs.append(Q("Что такое WAL (Write-Ahead Log) в PostgreSQL?",
    [A("Журнал предзаписи, обеспечивающий долговечность транзакций", True),
     A("Система управления доступом к данным", False),
     A("Кэш часто запрашиваемых результатов", False),
     A("Инструмент мониторинга производительности", False)]))

Qs.append(Q("Какие из перечисленных процессов связаны с обслуживанием буферного кеша и WAL?",
    [A("walwriter", True),
     A("checkpointer", True),
     A("background writer (bgwriter)", True),
     A("autovacuum launcher", False),
     A("logical replication launcher", False),
     A("pgbouncer", False)]))

Qs.append(Q("Что такое контрольная точка (checkpoint) в PostgreSQL?",
    [A("Периодический сброс всех грязных буферов на диск для ограничения объёма WAL при восстановлении", True),
     A("Аварийная остановка сервера при исчерпании места на диске", False),
     A("Проверка контрольных сумм всех страниц данных", False),
     A("Переключение на резервный сервер", False)]))

Qs.append(Q("Что означает параметр synchronous_commit = on?",
    [A("Журнальная запись гарантированно попадает на диск до подтверждения фиксации транзакции", True),
     A("Данные записываются на диск асинхронно фоновым процессом walwriter", False),
     A("Буферный кеш сбрасывается на диск при каждом запросе", False),
     A("Резервный сервер получает данные синхронно с основным", False)]))

# ========== Topic 08: Базы данных и схемы ==========
Qs.append(Q("Сколько баз данных создаётся по умолчанию при инициализации кластера?",
    [A("Три: postgres, template0, template1", True),
     A("Одна: postgres", False),
     A("Две: template0, template1", False),
     A("Четыре: postgres, template0, template1, public", False)]))

Qs.append(Q("Из какого шаблона по умолчанию создаются новые базы данных?",
    [A("template1", True),
     A("template0", False),
     A("postgres", False),
     A("default", False)]))

Qs.append(Q("Чем отличается шаблон template0 от template1?",
    [A("template0 не должен изменяться и используется для создания БД с нестандартной кодировкой; template1 используется по умолчанию", True),
     A("template0 содержит системные таблицы, template1 — пользовательские", False),
     A("template0 создаётся после template1 при инициализации", False),
     A("Различий нет, они полностью идентичны", False)]))

Qs.append(Q("Что такое схема в PostgreSQL?",
    [A("Пространство имён для объектов внутри базы данных", True),
     A("Физическое хранилище файлов данных", False),
     A("Журнал всех изменений в базе данных", False),
     A("Резервная копия базы данных", False)]))

Qs.append(Q("В какой схеме по умолчанию создаются новые объекты при подключении к базе данных?",
    [A("public", True),
     A("pg_catalog", False),
     A("information_schema", False),
     A("schema", False)]))

# ========== Topic 09: Системный каталог ==========
Qs.append(Q("В какой схеме находятся основные таблицы системного каталога?",
    [A("pg_catalog", True),
     A("information_schema", False),
     A("public", False),
     A("sys_catalog", False)]))

Qs.append(Q("Какой префикс имеют все таблицы системного каталога для предотвращения конфликтов имён?",
    [A("pg_", True),
     A("sys_", False),
     A("system_", False),
     A("meta_", False)]))

Qs.append(Q("В какой таблице системного каталога хранится описание таблиц, представлений, индексов и последовательностей?",
    [A("pg_class", True),
     A("pg_tables", False),
     A("pg_objects", False),
     A("pg_relation", False)]))

Qs.append(Q("Какой столбец в pg_class определяет тип объекта?",
    [A("relkind", True),
     A("reltype", False),
     A("relobj", False),
     A("relcategory", False)]))

Qs.append(Q("Какая команда psql показывает детальную информацию об объекте (таблице, представлении и т.д.)?",
    [A("\\d [имя_объекта]", True),
     A("\\info [имя_объекта]", False),
     A("\\desc [имя_объекта]", False),
     A("\\describe [имя_объекта]", False)]))

# ========== Topic 10: Табличные пространства ==========
Qs.append(Q("Какие два табличных пространства создаются при инициализации кластера?",
    [A("pg_default и pg_global", True),
     A("pg_data и pg_meta", False),
     A("pg_main и pg_system", False),
     A("pg_primary и pg_secondary", False)]))

Qs.append(Q("В каком каталоге хранятся данные табличного пространства pg_global?",
    [A("PGDATA/global/", True),
     A("PGDATA/base/", False),
     A("PGDATA/pg_tblspc/", False),
     A("PGDATA/pg_wal/", False)]))

Qs.append(Q("Какая команда psql показывает список табличных пространств?",
    [A("\\db", True),
     A("\\tsp", False),
     A("\\dblist", False),
     A("\\tablespaces", False)]))

Qs.append(Q("Что произойдёт при попытке удалить табличное пространство, в котором есть объекты?",
    [A("Ошибка — табличное пространство можно удалить только если оно пусто", True),
     A("Объекты автоматически переместятся в pg_default", False),
     A("Объекты будут удалены вместе с табличным пространством", False),
     A("Табличное пространство перейдёт в режим только для чтения", False)]))

Qs.append(Q("Какой параметр задаёт табличное пространство по умолчанию для временных таблиц?",
    [A("temp_tablespaces", True),
     A("default_temp_tablespace", False),
     A("temp_tablespace", False),
     A("pg_default_temp", False)]))

# ========== Topic 11: Организация данных (файлы, TOAST) ==========
Qs.append(Q("Какие слои (forks) существуют у обычного табличного объекта?",
    [A("main (данные), fsm (карта свободного пространства), vm (карта видимости)", True),
     A("main, index, toast", False),
     A("data, wal, undo", False),
     A("main, log, metadata", False)]))

Qs.append(Q("Что такое TOAST в PostgreSQL?",
    [A("Механизм хранения длинных значений за пределами основной страницы строки с поддержкой сжатия", True),
     A("Инструмент для резервного копирования больших таблиц", False),
     A("Тип индекса для текстовых данных", False),
     A("Система управления большими данными", False)]))

Qs.append(Q("Какие стратегии хранения (storage) поддерживаются для столбцов в TOAST?",
    [A("plain", True),
     A("extended", True),
     A("external", True),
     A("main", True),
     A("compressed", False),
     A("chunked", False)]))

Qs.append(Q("В какой схеме находятся TOAST-таблицы?",
    [A("pg_toast", True),
     A("pg_system", False),
     A("pg_largeobject", False),
     A("pg_largeobject_metadata", False)]))

Qs.append(Q("Какой размер файла (сегмента) используется при разбивке файлов объектов при превышении размера?",
    [A("1 Гбайт", True),
     A("256 Мбайт", False),
     A("512 Мбайт", False),
     A("2 Гбайта", False)]))

# ========== Topic 12: Мониторинг ==========
Qs.append(Q("В каком представлении PostgreSQL можно увидеть текущие активности всех подключённых пользователей?",
    [A("pg_stat_activity", True),
     A("pg_stat_process", False),
     A("pg_activity", False),
     A("pg_backend_status", False)]))

Qs.append(Q("Какой параметр необходимо включить для сбора статистики ввода-вывода?",
    [A("track_io_timing = on", True),
     A("track_io = on", False),
     A("io_monitoring = on", False),
     A("stats_track_io = on", False)]))

Qs.append(Q("Какие из перечисленных параметров управления статистикой включены по умолчанию?",
    [A("track_activities", True),
     A("track_counts", True),
     A("track_functions", False),
     A("track_io_timing", False),
     A("track_wal_io_timing", False)]))

Qs.append(Q("Что показывает столбец wait_event в представлении pg_stat_activity?",
    [A("Тип события, на котором процесс ожидает (например, Lock, IO, ClientRead)", True),
     A("Количество обработанных запросов", False),
     A("Имя базы данных", False),
     A("Время последнего запроса", False)]))

Qs.append(Q("Какая функция позволяет завершить (отклонить) сеанс другого пользователя?",
    [A("pg_terminate_backend(pid)", True),
     A("pg_cancel_backend(pid)", False),
     A("pg_stop_session(pid)", False),
     A("pg_kill_backend(pid)", False)]))

# ========== Topic 13: Управление доступом ==========
Qs.append(Q("Какой атрибут роли позволяет подключаться к серверу PostgreSQL?",
    [A("LOGIN", True),
     A("CONNECT", False),
     A("ACCESS", False),
     A("SESSION", False)]))

Qs.append(Q("Какой метод аутентификации в pg_hba.conf запрашивает имя пользователя у операционной системы?",
    [A("peer", True),
     A("trust", False),
     A("scram-sha-256", False),
     A("md5", False)]))

Qs.append(Q("Где хранится хеш-код паролей ролей в PostgreSQL?",
    [A("В системном каталоге pg_authid", True),
     A("В файле postgresql.conf", False),
     A("В файле pg_hba.conf", False),
     A("В каталоге PGDATA/pg_passwd/", False)]))

Qs.append(Q("Какая команда используется для выдачи привилегий в PostgreSQL?",
    [A("GRANT", True),
     A("ALLOW", False),
     A("PERMIT", False),
     A("AUTHORIZE", False)]))

Qs.append(Q("Что означает привилегия USAGE для схемы?",
    [A("Разрешает обращаться к объектам в этой схеме", True),
     A("Разрешает создавать объекты в схеме", False),
     A("Разрешает удалять схему", False),
     A("Разрешает подключаться к базе данных", False)]))

# ========== Topic 14: Резервное копирование ==========
Qs.append(Q("Какая утилита создаёт логическую резервную копию базы данных в виде SQL-скрипта?",
    [A("pg_dump", True),
     A("pg_dumpall", False),
     A("pg_basebackup", False),
     A("pg_restore", False)]))

Qs.append(Q("Какая утилита создаёт логическую копию всего кластера, включая роли и табличные пространства?",
    [A("pg_dumpall", True),
     A("pg_dump", False),
     A("pg_basebackup", False),
     A("pg_restore", False)]))

Qs.append(Q("Какая утилита создаёт физическую (горячую) резервную копию кластера?",
    [A("pg_basebackup", True),
     A("pg_dump", False),
     A("pg_dumpall", False),
     A("cp -r PGDATA backup/", False)]))

Qs.append(Q("Из какого шаблона необходимо создавать базу данных для восстановления из pg_dump?",
    [A("template0", True),
     A("template1", False),
     A("postgres", False),
     A("Любой шаблон подойдёт", False)]))

Qs.append(Q("Какой параметр WAL-уровня необходим для создания горячей резервной копии и физической репликации?",
    [A("wal_level = replica", True),
     A("wal_level = minimal", False),
     A("wal_level = logical", False),
     A("wal_level = archive", False)]))

# ========== Topic 15: Физическая репликация ==========
Qs.append(Q("Какой процесс на мастере отправляет журнальные записи реплике?",
    [A("walsender", True),
     A("walreceiver", False),
     A("walwriter", False),
     A("startup", False)]))

Qs.append(Q("Какой процесс на реплике получает и применяет журнальные записи от мастера?",
    [A("walreceiver", True),
     A("walsender", False),
     A("walwriter", False),
     A("checkpointer", False)]))

Qs.append(Q("Какая физическая репликация позволяет читать данные только (режим hot standby)?",
    [A("Реплика не позволяет изменения, только SELECT, COPY TO, курсоры", True),
     A("Реплика позволяет изменения, но не позволяет читать данные", False),
     A("Реплика полностью независима от мастера", False),
     A("Реплика позволяет DDL-команды, но не DML", False)]))

Qs.append(Q("Какую роль играет слот репликации (replication slot)?",
    [A("Предотвращает удаление WAL-файлов, пока они не прочитаны репликой", True),
     A("Шифрует передаваемые журнальные записи", False),
     A("Ускоряет запись WAL на реплике", False),
     A("Автоматически переключает мастер на реплику при сбое", False)]))

Qs.append(Q("Какой параметр определяет, синхронно или асинхронно мастер ждёт подтверждения от реплики?",
    [A("synchronous_commit", True),
     A("wal_level", False),
     A("max_wal_senders", False),
     A("hot_standby", False)]))

# ========== Topic 16: Логическая репликация ==========
Qs.append(Q("Какой WAL-уровень необходим для логической репликации?",
    [A("logical", True),
     A("replica", False),
     A("minimal", False),
     A("archive", False)]))

Qs.append(Q("Что такое публикация (publication) в логической репликации?",
    [A("Настройка на публикующем сервере, определяющая какие таблицы и изменения передаются подписчикам", True),
     A("Журнал всех SQL-команд, выполненных на сервере", False),
     A("Список всех подключённых реплик", False),
     A("Архив резервных копий таблиц", False)]))

Qs.append(Q("Что такое подписка (subscription) в логической репликации?",
    [A("Настройка на сервере-подписчике, определяющая откуда получать изменения", True),
     A("Разрешение на запись данных в таблицу", False),
     A("Метод аутентификации для репликации", False),
     A("Тип резервной копии", False)]))

Qs.append(Q("Какой идентификатор используется по умолчанию для определения старой версии строки при обновлении на подписчике?",
    [A("Столбцы первичного ключа", True),
     A("Все столбцы таблицы", False),
     A("Первый столбец таблицы", False),
     A("Столбец rowid", False)]))

Qs.append(Q("Какой тип команд DDL передаётся при логической репликации?",
    [A("DDL не передаётся, таблицы-приёмники создаются вручную на подписчике", True),
     A("Передаются все DDL-команды автоматически", False),
     A("Передаются только CREATE TABLE", False),
     A("Передаются только ALTER TABLE", False)]))

# ===== Dump JSON =====
dump_json(
    "PostgreSQL — Junior (DBA1)",
    "Тест Junior: 80 вопросов, основанных на материалах курса DBA1 (16 тем, по 5 вопросов)",
    Qs,
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "json", "General_Junior.json")
)
