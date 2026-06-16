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

    private Guid CurrentUserId => Guid.Parse(User.FindFirst(ClaimTypes.NameIdentifier)!.Value);

    private async Task<bool> IsTestAccessible(Guid testId)
    {
        var test = await _context.Tests.FindAsync(testId);
        return test != null && test.IsActive;
    }

    private async Task<bool> IsAttemptOwnedByUser(Guid attemptId)
    {
        var attempt = await _context.TestAttempts.FindAsync(attemptId);
        return attempt != null && attempt.UserId == CurrentUserId;
    }

    // Старт теста
    public async Task<IActionResult> Start(Guid testId)
    {
        if (!await IsTestAccessible(testId))
            return NotFound();

        // Проверяем, нет ли уже незавершённой попытки
        var existingAttempt = await _context.TestAttempts
            .FirstOrDefaultAsync(a => a.TestId == testId 
                && a.UserId == CurrentUserId 
                && a.Status == AttemptStatus.InProgress);

        if (existingAttempt != null)
        {
            return RedirectToAction(nameof(Question), new { attemptId = existingAttempt.Id, questionNumber = 1 });
        }

        var attempt = new TestAttempt
        {
            Id = Guid.NewGuid(),
            TestId = testId,
            UserId = CurrentUserId,
            StartedAt = DateTime.UtcNow,
            Status = AttemptStatus.InProgress
        };

        _context.TestAttempts.Add(attempt);

        _context.Logs.Add(new Log
        {
            Action = "Начало теста",
            EntityName = "TestAttempt",
            EntityId = attempt.Id.ToString(),
            UserId = CurrentUserId,
            Timestamp = DateTime.UtcNow
        });

        await _context.SaveChangesAsync();

        return RedirectToAction(nameof(Question), new { attemptId = attempt.Id, questionNumber = 1 });
    }

    // Отображение вопроса
    public async Task<IActionResult> Question(Guid attemptId, int questionNumber)
    {
        if (!await IsAttemptOwnedByUser(attemptId))
            return Forbid();

        var attempt = await _context.TestAttempts
            .Include(a => a.Test)
            .FirstOrDefaultAsync(a => a.Id == attemptId);

        if (attempt == null || attempt.Status == AttemptStatus.Completed)
            return RedirectToAction("Index", "Home");

        // Проверка таймаута
        if (attempt.Test?.TimeLimit > 0)
        {
            var elapsed = (DateTime.UtcNow - attempt.StartedAt).TotalSeconds;
            if (elapsed > attempt.Test.TimeLimit)
            {
                return RedirectToAction(nameof(Finish), new { attemptId });
            }
        }

        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .OrderBy(q => q.Order)
            .ToListAsync();

        if (questionNumber < 1 || questionNumber > questions.Count)
            return RedirectToAction(nameof(Finish), new { attemptId });

        var question = questions[questionNumber - 1];

        // Загружаем ответы вопроса
        var answers = await _context.Answers
            .Where(a => a.QuestionId == question.Id)
            .ToListAsync();

        // Загружаем ответы пользователя для этого вопроса
        var userAnswers = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == question.Id)
            .ToListAsync();

        // Помечаем какие вопросы уже отвечены
        var answeredQuestionIds = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId)
            .Select(ua => ua.QuestionId)
            .Distinct()
            .ToListAsync();

        ViewBag.Answers = answers;
        ViewBag.UserAnswers = userAnswers;
        ViewBag.Attempt = attempt;
        ViewBag.QuestionNumber = questionNumber;
        ViewBag.TotalQuestions = questions.Count;
        ViewBag.AnsweredQuestionIds = answeredQuestionIds;
        ViewBag.Questions = questions;

        return View(question);
    }

    // Автосохранение ответа (AJAX)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> SaveAnswer(Guid attemptId, Guid questionId, Guid[]? selectedAnswers, string? rawValue)
    {
        if (!await IsAttemptOwnedByUser(attemptId))
            return Forbid();

        var attempt = await _context.TestAttempts.FindAsync(attemptId);
        if (attempt == null || attempt.Status == AttemptStatus.Completed) return BadRequest();

        // Проверка таймаута
        if (attempt.Test?.TimeLimit > 0)
        {
            var elapsed = (DateTime.UtcNow - attempt.StartedAt).TotalSeconds;
            if (elapsed > attempt.Test.TimeLimit)
            {
                return BadRequest(new { error = "timeout" });
            }
        }

        // Удаляем старые ответы на этот вопрос в этой попытке
        var oldAnswers = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == questionId)
            .ToListAsync();
        _context.UserAnswers.RemoveRange(oldAnswers);

        bool hasAnswer = false;

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
            hasAnswer = true;
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
            hasAnswer = true;
        }

        await _context.SaveChangesAsync();

        return Ok(new { saved = true, hasAnswer });
    }

    // Завершение теста
    public async Task<IActionResult> Finish(Guid attemptId)
    {
        if (!await IsAttemptOwnedByUser(attemptId))
            return Forbid();

        var attempt = await _context.TestAttempts
            .Include(a => a.Test)
            .FirstOrDefaultAsync(a => a.Id == attemptId);

        if (attempt == null || attempt.Status == AttemptStatus.Completed)
            return RedirectToAction("Index", "Home");

        // Проверка: есть ли хотя бы один ответ
        var hasAnyAnswer = await _context.UserAnswers
            .AnyAsync(ua => ua.AttemptId == attemptId);

        // Расчет баллов
        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .ToListAsync();

        int correctCount = 0;
        var questionResults = new List<QuestionResultDetail>();

        foreach (var q in questions)
        {
            var correctAnswers = await _context.Answers
                .Where(a => a.QuestionId == q.Id && a.IsCorrect)
                .ToListAsync();

            var userAnswers = await _context.UserAnswers
                .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == q.Id)
                .ToListAsync();

            bool isCorrect = false;

            if (q.Type == QuestionType.Numeric)
            {
                var correctAnswer = correctAnswers.FirstOrDefault();
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
                var userSelectedIds = userAnswers
                    .Where(ua => ua.SelectedAnswerId.HasValue)
                    .Select(ua => ua.SelectedAnswerId!.Value)
                    .ToList();
                var correctIds = correctAnswers.Select(a => a.Id).ToList();

                isCorrect = correctIds.Count == userSelectedIds.Count &&
                            !correctIds.Except(userSelectedIds).Any();
            }

            if (isCorrect) correctCount++;

            questionResults.Add(new QuestionResultDetail
            {
                Question = q,
                IsCorrect = isCorrect,
                UserAnswers = userAnswers,
                CorrectAnswers = correctAnswers
            });

            foreach (var ua in userAnswers) ua.IsCorrect = isCorrect;
        }

        attempt.Score = questions.Count > 0
            ? Math.Round((double)correctCount / questions.Count * 100, 2)
            : 0;
        attempt.FinishedAt = DateTime.UtcNow;
        attempt.Status = AttemptStatus.Completed;

        _context.Logs.Add(new Log
        {
            Action = $"Завершение теста. Результат: {attempt.Score}%",
            EntityName = "TestAttempt",
            EntityId = attempt.Id.ToString(),
            UserId = CurrentUserId,
            Timestamp = DateTime.UtcNow
        });

        await _context.SaveChangesAsync();

        ViewBag.QuestionResults = questionResults;
        ViewBag.CorrectCount = correctCount;
        ViewBag.TotalCount = questions.Count;

        return View(attempt);
    }
}

public class QuestionResultDetail
{
    public Question Question { get; set; } = null!;
    public bool IsCorrect { get; set; }
    public List<UserAnswer> UserAnswers { get; set; } = null!;
    public List<Answer> CorrectAnswers { get; set; } = null!;
}
