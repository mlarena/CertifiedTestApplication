using System.ComponentModel.DataAnnotations;

namespace CertifiedTestApplication.Models.Entities;

public class Category
{
    public int Id { get; set; }
    [Required, MaxLength(200)]
    public string Name { get; set; } = string.Empty;
}
