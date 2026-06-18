using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using CertifiedTestApplication.Models.ViewModels;

namespace CertifiedTestApplication.Services;

public class TestEvaluationService : ITestEvaluationService
{
    private readonly ApplicationDbContext _context;

    public TestEvaluationService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<(int CorrectCount, int TotalCount, List<QuestionResultDetail> Results)> EvaluateTestAsync(Guid attemptId)
    {
        var attempt = await _context.TestAttempts
            .FirstOrDefaultAsync(a => a.Id == attemptId);

        if (attempt == null)
            return (0, 0, new List<QuestionResultDetail>());

        var questions = await _context.Questions
            .Where(q => q.TestId == attempt.TestId)
            .OrderBy(q => q.Order)
            .ThenBy(q => q.Id)
            .ToListAsync();

        int correctCount = 0;
        var questionResults = new List<QuestionResultDetail>();

        foreach (var q in questions)
        {
            var allAnswers = await _context.Answers
                .Where(a => a.QuestionId == q.Id)
                .ToListAsync();

            var correctAnswers = allAnswers.Where(a => a.IsCorrect).ToList();

            var userAnswers = await _context.UserAnswers
                .Where(ua => ua.AttemptId == attemptId && ua.QuestionId == q.Id)
                .ToListAsync();

            bool isCorrect = EvaluateQuestion(q, correctAnswers, userAnswers);

            if (isCorrect) correctCount++;

            questionResults.Add(new QuestionResultDetail
            {
                Question = q,
                IsCorrect = isCorrect,
                UserAnswers = userAnswers,
                CorrectAnswers = correctAnswers,
                AllAnswers = allAnswers
            });

            foreach (var ua in userAnswers) ua.IsCorrect = isCorrect;
        }

        return (correctCount, questions.Count, questionResults);
    }

    private static bool EvaluateQuestion(Question question, List<Answer> correctAnswers, List<UserAnswer> userAnswers)
    {
        if (question.Type == QuestionType.Numeric)
        {
            return EvaluateNumericQuestion(correctAnswers, userAnswers);
        }

        return EvaluateChoiceQuestion(correctAnswers, userAnswers);
    }

    private static bool EvaluateNumericQuestion(List<Answer> correctAnswers, List<UserAnswer> userAnswers)
    {
        var correctAnswer = correctAnswers.FirstOrDefault();
        var userVal = userAnswers.FirstOrDefault()?.RawValue;

        if (correctAnswer?.NumericValue == null || userVal == null)
            return false;

        if (double.TryParse(userVal.Replace(",", "."), System.Globalization.NumberStyles.Any,
            System.Globalization.CultureInfo.InvariantCulture, out double val))
        {
            return Math.Abs(val - correctAnswer.NumericValue.Value) < 0.01;
        }

        return false;
    }

    private static bool EvaluateChoiceQuestion(List<Answer> correctAnswers, List<UserAnswer> userAnswers)
    {
        var userSelectedIds = userAnswers
            .Where(ua => ua.SelectedAnswerId.HasValue)
            .Select(ua => ua.SelectedAnswerId!.Value)
            .ToHashSet();

        var correctIds = correctAnswers.Select(a => a.Id).ToHashSet();

        return correctIds.Count == userSelectedIds.Count && correctIds.SetEquals(userSelectedIds);
    }
}
