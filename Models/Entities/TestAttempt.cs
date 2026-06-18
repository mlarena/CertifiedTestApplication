using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
