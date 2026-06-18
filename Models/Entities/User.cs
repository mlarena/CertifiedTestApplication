using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

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
