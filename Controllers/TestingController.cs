using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;

namespace CertifiedTestApplication.Controllers;

[Authorize]
public class TestingController : Controller
{
    private readonly ApplicationDbContext _context;

    public TestingController(ApplicationDbContext context)
    {
        _context = context;
    }

    // Старт теста
    public async Task<IActionResult> Start(Guid testId)
    {
        var test = await _context.Tests.FindAsync(testId);
        if (test == null || !test.IsActive) return NotFound();

        var userId = Guid.Parse(User.FindFirst(ClaimTypes.NameIdentifier)!.Value);

        // Создаем новую попытку
        var attempt = new TestAttempt
        {
            Id = Guid.NewGuid(),
            TestId = testId,
            UserId = userId,
            StartedAt = DateTime.UtcNow,
            Status = AttemptStatus.InProgress
        };

        _context.TestAttempts.Add(attempt);
        await _context.SaveChangesAsync();

        return RedirectToAction(nameof(Question), new { attemptId = attempt.Id, questionNumber = 1 });
    }

    // Отображение вопроса
    public async Task<IActionResult> Question(Guid attemptId, int questionNumber)
    {
        var attempt = await _context.TestAttempts
            .Include(a => a.Test)
            .FirstOrDefaultAsync(a => a.Id == attemptId);

        if (attempt == null || attempt.Status == AttemptStatus.Completed) 
            return RedirectToAction("Index", "Home");

        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .OrderBy(q => q.Order)
            .ToListAsync();

        if (questionNumber < 1 || questionNumber > questions.Count)
            return RedirectToAction(nameof(Finish), new { attemptId });

        var question = questions[questionNumber - 1];
        
        ViewBag.Answers = await _context.Answers
            .Where(a => a.QuestionId == question.Id)
            .ToListAsync();
            
        ViewBag.UserAnswers = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == question.Id)
            .ToListAsync();

        ViewBag.Attempt = attempt;
        ViewBag.QuestionNumber = questionNumber;
        ViewBag.TotalQuestions = questions.Count;

        return View(question);
    }

    // Автосохранение ответа (AJAX)
    [HttpPost]
    public async Task<IActionResult> SaveAnswer(Guid attemptId, Guid questionId, Guid[] selectedAnswers, string? rawValue)
    {
        var attempt = await _context.TestAttempts.FindAsync(attemptId);
        if (attempt == null || attempt.Status == AttemptStatus.Completed) return BadRequest();

        // Удаляем старые ответы на этот вопрос в этой попытке
        var oldAnswers = _context.UserAnswers.Where(ua => ua.AttemptId == attemptId && ua.QuestionId == questionId);
        _context.UserAnswers.RemoveRange(oldAnswers);

        if (selectedAnswers != null && selectedAnswers.Length > 0)
        {
            foreach (var ansId in selectedAnswers)
            {
                _context.UserAnswers.Add(new UserAnswer
                {
                    Id = Guid.NewGuid(),
                    AttemptId = attemptId,
                    QuestionId = questionId,
                    SelectedAnswerId = ansId,
                    AnsweredAt = DateTime.UtcNow
                });
            }
        }
        else if (!string.IsNullOrEmpty(rawValue))
        {
            _context.UserAnswers.Add(new UserAnswer
            {
                Id = Guid.NewGuid(),
                AttemptId = attemptId,
                QuestionId = questionId,
                RawValue = rawValue,
                AnsweredAt = DateTime.UtcNow
            });
        }

        await _context.SaveChangesAsync();
        return Ok();
    }

    // Завершение теста
    public async Task<IActionResult> Finish(Guid attemptId)
    {
        var attempt = await _context.TestAttempts
            .Include(a => a.Test)
            .FirstOrDefaultAsync(a => a.Id == attemptId);

        if (attempt == null || attempt.Status == AttemptStatus.Completed) 
            return RedirectToAction("Index", "Home");

        // Расчет баллов
        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .Include(q => q.Test)
            .ToListAsync();

        int correctCount = 0;

        foreach (var q in questions)
        {
            var correctAnswers = await _context.Answers
                .Where(a => a.QuestionId == q.Id && a.IsCorrect)
                .Select(a => a.Id)
                .ToListAsync();

            var userAnswers = await _context.UserAnswers
                .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == q.Id)
                .ToListAsync();

            bool isCorrect = false;

            if (q.Type == QuestionType.Numeric)
            {
                var correctAnswer = await _context.Answers.FirstOrDefaultAsync(a => a.QuestionId == q.Id);
                var userVal = userAnswers.FirstOrDefault()?.RawValue;
                if (correctAnswer != null && userVal != null && 
                    double.TryParse(userVal.Replace(",", "."), out double val) && 
                    val == correctAnswer.NumericValue)
                {
                    isCorrect = true;
                }
            }
            else
            {
                var userSelectedIds = userAnswers.Select(ua => ua.SelectedAnswerId ?? Guid.Empty).ToList();
                // Проверка: все правильные выбраны И нет лишних
                isCorrect = correctAnswers.Count == userSelectedIds.Count && 
                            !correctAnswers.Except(userSelectedIds).Any();
            }

            if (isCorrect) correctCount++;
            
            // Обновляем статус правильности в UserAnswers для истории
            foreach(var ua in userAnswers) ua.IsCorrect = isCorrect;
        }

        attempt.Score = Math.Round((double)correctCount / questions.Count * 100, 2);
        attempt.FinishedAt = DateTime.UtcNow;
        attempt.Status = AttemptStatus.Completed;

        await _context.SaveChangesAsync();

        return View(attempt);
    }
}
