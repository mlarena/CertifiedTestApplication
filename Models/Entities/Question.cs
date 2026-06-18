using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
