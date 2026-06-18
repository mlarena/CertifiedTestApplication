using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using CertifiedTestApplication.Models.ViewModels;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;

namespace CertifiedTestApplication.Controllers;

[Authorize]
public class ReportsController : Controller
{
    private readonly ApplicationDbContext _context;

    public ReportsController(ApplicationDbContext context)
    {
        _context = context;
    }

    // Личный кабинет пользователя
    public async Task<IActionResult> MyResults()
    {
        var userId = Guid.Parse(User.FindFirst(ClaimTypes.NameIdentifier)!.Value);
        var attempts = await _context.TestAttempts
            .Include(a => a.Test)
            .Where(a => a.UserId == userId)
            .OrderByDescending(a => a.StartedAt)
            .ToListAsync();
        return View(attempts);
    }

    // Журнал попыток (для Админа и Инженера)
    [Authorize(Roles = "Admin,Engineer")]
    public async Task<IActionResult> Journal(string? group, string? status)
    {
        var query = _context.TestAttempts
            .Include(a => a.Test)
            .Include(a => a.User)
            .AsQueryable();

        if (!string.IsNullOrEmpty(status))
        {
            if (status == "Passed") query = query.Where(a => a.Score >= 80);
            if (status == "Failed") query = query.Where(a => a.Score < 80);
        }

        var attempts = await query.OrderByDescending(a => a.StartedAt).ToListAsync();
        return View(attempts);
    }

    // Разбор ошибок
    public async Task<IActionResult> Details(Guid id)
    {
        var attempt = await _context.TestAttempts
            .Include(a => a.Test)
            .Include(a => a.User)
            .FirstOrDefaultAsync(a => a.Id == id);

        if (attempt == null) return NotFound();

        // Проверка прав: только владелец или админ/инженер
        var userId = Guid.Parse(User.FindFirst(ClaimTypes.NameIdentifier)!.Value);
        if (attempt.UserId != userId && !User.IsInRole("Admin") && !User.IsInRole("Engineer"))
            return Forbid();

        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .OrderBy(q => q.Order)
            .ToListAsync();

        var details = new List<QuestionResultViewModel>();

        foreach (var q in questions)
        {
            var answers = await _context.Answers.Where(a => a.QuestionId == q.Id).ToListAsync();
            var userAnswers = await _context.UserAnswers
                .Where(ua => ua.AttemptId == id && ua.QuestionId == q.Id)
                .ToListAsync();

            details.Add(new QuestionResultViewModel
            {
                Question = q,
                Answers = answers,
                UserAnswers = userAnswers,
                IsCorrect = userAnswers.Any() && userAnswers.First().IsCorrect
            });
        }

        ViewBag.Attempt = attempt;
        return View(details);
    }

    [Authorize(Roles = "Admin")]
    public async Task<IActionResult> Logs()
    {
        var logs = await _context.Logs
            .Include(l => l.User)
            .OrderByDescending(l => l.Timestamp)
            .Take(500)
            .ToListAsync();
        return View(logs);
    }
}
