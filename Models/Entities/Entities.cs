using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

public class Role
{
    public int Id { get; set; }
    [Required, MaxLength(50)]
    public string Name { get; set; } = string.Empty;
}

public class User
{
    public Guid Id { get; set; }
    public int RoleId { get; set; }
    public Role? Role { get; set; }

    [Required, MaxLength(100)]
    public string Login { get; set; } = string.Empty;
    
    [Required]
    public string PasswordHash { get; set; } = string.Empty;
    
    [Required, MaxLength(250)]
    public string FullName { get; set; } = string.Empty;
    
    public bool IsBlocked { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class Category
{
    public int Id { get; set; }
    [Required, MaxLength(200)]
    public string Name { get; set; } = string.Empty;
}

public class Test
{
    public Guid Id { get; set; }
    public int CategoryId { get; set; }
    public Category? Category { get; set; }
    
    public Guid AuthorId { get; set; }
    public User? Author { get; set; }

    [Required, MaxLength(500)]
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    
    public int TimeLimit { get; set; } // в секундах
    public bool IsActive { get; set; }
    public bool CanReturnToQuestion { get; set; } = true;
    
    public List<Question>? Questions { get; set; }
    public List<TestAttempt>? Attempts { get; set; }
}

public enum QuestionType
{
    Single = 1,
    Multiple = 2,
    Numeric = 3
}

public class Question
{
    public Guid Id { get; set; }
    public Guid TestId { get; set; }
    public Test? Test { get; set; }
    
    public QuestionType Type { get; set; }
    
    [Required]
    public string Text { get; set; } = string.Empty;
    public string? ImagePath { get; set; }
    public int Order { get; set; }
    
    public List<Answer>? Answers { get; set; }
}

public class Answer
{
    public Guid Id { get; set; }
    public Guid QuestionId { get; set; }
    public Question? Question { get; set; }
    
    [Required]
    public string Text { get; set; } = string.Empty;
    public bool IsCorrect { get; set; }
    public double? NumericValue { get; set; }
}

public enum AttemptStatus
{
    InProgress = 1,
    Completed = 2
}

public class TestAttempt
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    
    public Guid TestId { get; set; }
    public Test? Test { get; set; }
    
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? FinishedAt { get; set; }
    public double? Score { get; set; }
    public AttemptStatus Status { get; set; } = AttemptStatus.InProgress;
}

public class UserAnswer
{
    public Guid Id { get; set; }
    public Guid AttemptId { get; set; }
    public TestAttempt? Attempt { get; set; }
    
    public Guid QuestionId { get; set; }
    public Question? Question { get; set; }
    
    public Guid? SelectedAnswerId { get; set; }
    public string? RawValue { get; set; }
    public bool IsCorrect { get; set; }
    public DateTime AnsweredAt { get; set; } = DateTime.UtcNow;
}

public class Log
{
    public long Id { get; set; }
    public Guid? UserId { get; set; }
    public User? User { get; set; }
    
    [Required]
    public string Action { get; set; } = string.Empty;
    public string? EntityName { get; set; }
    public string? EntityId { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? IPAddress { get; set; }
}
