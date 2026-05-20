# План реализации АСТП (Автоматизированная система технического тестирования)

## Этап 1: Проектирование и настройка БД (PostgreSQL)

### 1.1. Структура таблиц

**1. Roles (Роли)**
- `Id` (int, PK)
- `Name` (string: Admin, Engineer, User)

**2. Users (Пользователи)**
- `Id` (Guid, PK)
- `RoleId` (int, FK)
- `Login` (string, unique)
- `PasswordHash` (string)
- `FullName` (string)
- `IsBlocked` (bool)
- `CreatedAt` (DateTime)

**3. Categories (Категории)**
- `Id` (int, PK)
- `Name` (string)

**4. Tests (Тесты)**
- `Id` (Guid, PK)
- `CategoryId` (int, FK)
- `AuthorId` (Guid, FK)
- `Title` (string)
- `Description` (string)
- `TimeLimit` (int, в секундах, общий или на вопрос)
- `IsActive` (bool)
- `CanReturnToQuestion` (bool, default: true)

**5. Questions (Вопросы)**
- `Id` (Guid, PK)
- `TestId` (Guid, FK)
- `QuestionType` (int: Single, Multiple, Numeric)
- `Text` (string)
- `ImagePath` (string, null)
- `Order` (int)
- `Tolerance` (double, null - не используется, точное совпадение)

**6. Answers (Варианты ответов)**- `Id` (Guid, PK)
- `QuestionId` (Guid, FK)
- `Text` (string)
- `IsCorrect` (bool)
- `NumericValue` (double, null - для сравнения в числовом вводе)

**7. TestAttempts (Попытки тестирования)**
- `Id` (Guid, PK)
- `UserId` (Guid, FK)
- `TestId` (Guid, FK)
- `StartedAt` (DateTime)
- `FinishedAt` (DateTime, null)
- `Score` (double, null)
- `Status` (int: InProgress, Completed)

**8. UserAnswers (Ответы пользователя - для автосохранения)**- `Id` (Guid, PK)
- `AttemptId` (Guid, FK)
- `QuestionId` (Guid, FK)
- `SelectedAnswerId` (Guid, FK, null)
- `RawValue` (string, null - для числового ввода)
- `IsCorrect` (bool)
- `AnsweredAt` (DateTime)

**9. Logs (Логирование)**
- `Id` (long, PK)
- `UserId` (Guid, FK, null)
- `Action` (string)
- `EntityName` (string)
- `EntityId` (string)
- `Timestamp` (DateTime)
- `IPAddress` (string)

### 1.2. Хранение файлов
- Изображения к вопросам: `wwwroot/uploads/questions/`
- Имена файлов: Guid для исключения конфликтов.

### 1.3. Технический стек БД
- Entity Framework Core
- Npgsql.EntityFrameworkCore.PostgreSQL
- Fluent API для настройки связей

---

## Этап 2: Инфраструктура и Аутентификация

### 2.1. Базовая настройка
- Подключение NuGet пакетов (Npgsql, EF Core).
- Создание `ApplicationDbContext`.
- Настройка Connection String в `appsettings.json`.

### 2.2. Своя система авторизации
- Middleware для Cookie Authentication.
- Сервис для хэширования паролей (BCrypt или SHA256+Salt).
- `AccountController` (Login, Logout).
- Атрибуты доступа по ролям (`[Authorize(Roles = "Admin")]`).

### 2.3. Логирование
- Реализация `LogService` для записи действий в таблицу `Logs`.

---

## Следующие шаги (для обсуждения):
- **Этап 3**: Разработка интерфейса администратора (Управление пользователями и категориями).
- **Этап 4**: Конструктор тестов (Инженерный режим).
- **Этап 5**: Движок тестирования (Пользовательский режим + автосохранение).
- **Этап 6**: Отчеты и аналитика.
