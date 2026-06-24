using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<Role> Roles { get; set; }
    public DbSet<User> Users { get; set; }
    public DbSet<Category> Categories { get; set; }
    public DbSet<Test> Tests { get; set; }
    public DbSet<Question> Questions { get; set; }
    public DbSet<Answer> Answers { get; set; }
    public DbSet<TestAttempt> TestAttempts { get; set; }
    public DbSet<UserAnswer> UserAnswers { get; set; }
    public DbSet<Log> Logs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Настройка уникальности логина
        modelBuilder.Entity<User>()
            .HasIndex(u => u.Login)
            .IsUnique();

        // Настройка связей (каскадное удаление при необходимости)
        modelBuilder.Entity<Question>()
            .HasOne(q => q.Test)
            .WithMany(t => t.Questions)
            .HasForeignKey(q => q.TestId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Answer>()
            .HasOne(a => a.Question)
            .WithMany(q => q.Answers)
            .HasForeignKey(a => a.QuestionId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<TestAttempt>()
            .HasOne(a => a.Test)
            .WithMany(t => t.Attempts)
            .HasForeignKey(a => a.TestId)
            .OnDelete(DeleteBehavior.Cascade);
            
        // Начальные данные для ролей
        modelBuilder.Entity<Role>().HasData(
            new Role { Id = 1, Name = "Admin" },
            new Role { Id = 2, Name = "Engineer" },
            new Role { Id = 3, Name = "User" }
        );
    }
}
