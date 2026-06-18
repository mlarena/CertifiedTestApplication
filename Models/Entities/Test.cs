using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
    
    public int TimeLimit { get; set; }
    public bool IsActive { get; set; }
    public bool CanReturnToQuestion { get; set; } = true;
    
    public List<Question>? Questions { get; set; }
    public List<TestAttempt>? Attempts { get; set; }
}
