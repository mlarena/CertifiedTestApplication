using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using CertifiedTestApplication.Models.ViewModels;
using CertifiedTestApplication.Services;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;

namespace CertifiedTestApplication.Controllers;

[Authorize]
public class TestingController : Controller
{
    private readonly ApplicationDbContext _context;
    private readonly ITestEvaluationService _evaluationService;

    public TestingController(ApplicationDbContext context, ITestEvaluationService evaluationService)
    {
        _context = context;
        _evaluationService = evaluationService;
    }

    private Guid CurrentUserId => Guid.Parse(User.FindFirst(ClaimTypes.NameIdentifier)!.Value);

    private async Task<(TestAttempt? Attempt, bool IsBlocked, string? Error)> LoadAttemptWithChecks(Guid attemptId)
    {
        var user = await _context.Users.FindAsync(CurrentUserId);
        if (user != null && user.IsBlocked)
            return (null, true, "blocked");

        var attempt = await _context.TestAttempts
            .Include(a => a.Test)
            .FirstOrDefaultAsync(a => a.Id == attemptId);

        if (attempt == null || attempt.UserId != CurrentUserId)
            return (null, false, "notfound");

        return (attempt, false, null);
    }

    // Старт теста
    public async Task<IActionResult> Start(Guid testId)
    {
        var test = await _context.Tests.FindAsync(testId);
        if (test == null || !test.IsActive)
            return NotFound();

        var questionCount = await _context.Questions.CountAsync(q => q.TestId == testId);
        if (questionCount == 0)
        {
            TempData["Error"] = "Тест не содержит вопросов";
            return RedirectToAction("Index", "Home");
        }

        var existingAttempt = await _context.TestAttempts
            .FirstOrDefaultAsync(a => a.TestId == testId
                && a.UserId == CurrentUserId
                && a.Status == AttemptStatus.InProgress);

        if (existingAttempt != null)
        {
            var answeredIds = await _context.UserAnswers
                .Where(ua => ua.AttemptId == existingAttempt.Id)
                .Select(ua => ua.QuestionId)
                .Distinct()
                .ToListAsync();

            var firstQuestion = await _context.Questions
                .Where(q => q.TestId == testId)
                .OrderBy(q => q.Order)
                .ThenBy(q => q.Id)
                .FirstOrDefaultAsync();

            int resumeNumber = 1;
            if (firstQuestion != null)
            {
                var allQuestions = await _context.Questions
                    .Where(q => q.TestId == testId)
                    .OrderBy(q => q.Order)
                    .ThenBy(q => q.Id)
                    .ToListAsync();

                var firstUnanswered = allQuestions
                    .FirstOrDefault(q => !answeredIds.Contains(q.Id));

                if (firstUnanswered != null)
                    resumeNumber = allQuestions.IndexOf(firstUnanswered) + 1;
                else
                    resumeNumber = allQuestions.Count;
            }

            return RedirectToAction(nameof(Question), new { attemptId = existingAttempt.Id, questionNumber = resumeNumber });
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
        var (attempt, isBlocked, error) = await LoadAttemptWithChecks(attemptId);
        if (isBlocked) return RedirectToAction("AccessDenied", "Account");
        if (error == "notfound" || attempt == null) return NotFound();
        if (attempt.Status == AttemptStatus.Completed)
            return RedirectToAction("Index", "Home");

        if (attempt.Test?.TimeLimit > 0)
        {
            var elapsed = (DateTime.UtcNow - attempt.StartedAt).TotalSeconds;
            if (elapsed > attempt.Test.TimeLimit)
                return RedirectToAction(nameof(Finish), new { attemptId });
        }

        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .OrderBy(q => q.Order)
            .ThenBy(q => q.Id)
            .ToListAsync();

        if (questionNumber < 1 || questionNumber > questions.Count)
            return RedirectToAction(nameof(Finish), new { attemptId });

        if (!attempt.Test!.CanReturnToQuestion)
        {
            var answeredIds = await _context.UserAnswers
                .Where(ua => ua.AttemptId == attemptId)
                .Select(ua => ua.QuestionId)
                .Distinct()
                .ToListAsync();

            var maxAnsweredIndex = -1;
            for (int i = 0; i < questions.Count; i++)
            {
                if (answeredIds.Contains(questions[i].Id))
                    maxAnsweredIndex = i;
            }

            if (questionNumber > maxAnsweredIndex + 2)
            {
                var redirectNumber = Math.Min(maxAnsweredIndex + 2, questions.Count);
                return RedirectToAction(nameof(Question), new { attemptId, questionNumber = redirectNumber });
            }
        }

        var question = questions[questionNumber - 1];

        var answers = await _context.Answers
            .Where(a => a.QuestionId == question.Id)
            .ToListAsync();

        var userAnswers = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == question.Id)
            .ToListAsync();

        var allAnsweredIds = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId)
            .Select(ua => ua.QuestionId)
            .Distinct()
            .ToListAsync();

        ViewBag.Answers = answers;
        ViewBag.UserAnswers = userAnswers;
        ViewBag.Attempt = attempt;
        ViewBag.QuestionNumber = questionNumber;
        ViewBag.TotalQuestions = questions.Count;
        ViewBag.AnsweredQuestionIds = allAnsweredIds;
        ViewBag.Questions = questions;

        return View(question);
    }

    // Автосохранение ответа (AJAX)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> SaveAnswer(Guid attemptId, Guid questionId, Guid[]? selectedAnswers, string? rawValue)
    {
        var (attempt, isBlocked, error) = await LoadAttemptWithChecks(attemptId);
        if (isBlocked) return Forbid();
        if (error != null || attempt == null || attempt.Status == AttemptStatus.Completed)
            return BadRequest();

        if (attempt.Test?.TimeLimit > 0)
        {
            var elapsed = (DateTime.UtcNow - attempt.StartedAt).TotalSeconds;
            if (elapsed > attempt.Test.TimeLimit)
                return BadRequest(new { error = "timeout" });
        }

        var question = await _context.Questions.FirstOrDefaultAsync(q => q.Id == questionId && q.TestId == attempt.TestId);
        if (question == null) return BadRequest();

        var oldAnswers = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == questionId)
            .ToListAsync();
        _context.UserAnswers.RemoveRange(oldAnswers);

        bool hasAnswer = false;

        if (selectedAnswers != null && selectedAnswers.Length > 0)
        {
            var validAnswerIds = await _context.Answers
                .Where(a => a.QuestionId == questionId)
                .Select(a => a.Id)
                .ToListAsync();

            foreach (var ansId in selectedAnswers.Where(id => validAnswerIds.Contains(id)))
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
                RawValue = rawValue.Length > 500 ? rawValue.Substring(0, 500) : rawValue,
                AnsweredAt = DateTime.UtcNow
            });
            hasAnswer = true;
        }

        await _context.SaveChangesAsync();

        return Ok(new { saved = true, hasAnswer });
    }

    [HttpGet]
    public async Task<IActionResult> GetAnsweredCount(Guid attemptId)
    {
        var (attempt, isBlocked, error) = await LoadAttemptWithChecks(attemptId);
        if (attempt == null) return BadRequest();

        var count = await _context.UserAnswers
            .Where(ua => ua.AttemptId == attemptId)
            .Select(ua => ua.QuestionId)
            .Distinct()
            .CountAsync();

        return Ok(new { count });
    }

    // Завершение теста (GET) — для автоматического завершения по таймауту
    public async Task<IActionResult> Finish(Guid attemptId)
    {
        var (attempt, isBlocked, error) = await LoadAttemptWithChecks(attemptId);
        if (isBlocked) return RedirectToAction("AccessDenied", "Account");
        if (error != null || attempt == null)
            return RedirectToAction("Index", "Home");

        if (attempt.Status == AttemptStatus.Completed)
            return RedirectToAction("Index", "Home");

        return await ProcessFinish(attempt, attemptId);
    }

    // Завершение теста (POST) — для ручного завершения пользователем
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> FinishPost(Guid attemptId)
    {
        var (attempt, isBlocked, error) = await LoadAttemptWithChecks(attemptId);
        if (isBlocked) return RedirectToAction("AccessDenied", "Account");
        if (error != null || attempt == null)
            return RedirectToAction("Index", "Home");

        if (attempt.Status == AttemptStatus.Completed)
            return RedirectToAction("Index", "Home");

        return await ProcessFinish(attempt, attemptId);
    }

    private async Task<IActionResult> ProcessFinish(TestAttempt attempt, Guid attemptId)
    {
        var forceFinish = false;
        if (attempt.Test?.TimeLimit > 0)
        {
            var elapsed = (DateTime.UtcNow - attempt.StartedAt).TotalSeconds;
            if (elapsed > attempt.Test.TimeLimit)
                forceFinish = true;
        }

        var (correctCount, totalCount, questionResults) = await _evaluationService.EvaluateTestAsync(attemptId);

        attempt.Score = totalCount > 0
            ? Math.Round((double)correctCount / totalCount * 100, 2)
            : 0;
        attempt.FinishedAt = DateTime.UtcNow;
        attempt.Status = AttemptStatus.Completed;

        _context.Logs.Add(new Log
        {
            Action = $"Завершение теста. Результат: {attempt.Score}%" + (forceFinish ? " (таймаут)" : ""),
            EntityName = "TestAttempt",
            EntityId = attempt.Id.ToString(),
            UserId = CurrentUserId,
            Timestamp = DateTime.UtcNow
        });

        await _context.SaveChangesAsync();

        ViewBag.QuestionResults = questionResults;
        ViewBag.CorrectCount = correctCount;
        ViewBag.TotalCount = totalCount;
        ViewBag.ForceFinish = forceFinish;

        return View("Finish", attempt);
    }
}
