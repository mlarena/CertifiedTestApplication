using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
