using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
