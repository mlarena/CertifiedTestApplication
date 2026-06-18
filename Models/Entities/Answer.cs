using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
