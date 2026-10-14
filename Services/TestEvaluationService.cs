using System.Globalization;
using System.Text.RegularExpressions;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using CertifiedTestApplication.Models.ViewModels;

namespace CertifiedTestApplication.Services;

public class TestEvaluationService : ITestEvaluationService
{
    // Patterns for parsing numeric answers with units, ranges, and exponents
    private static readonly Regex PowerPattern = new(@"(\d+(?:[.,]\d+)?)\s*\^\s*(\d+(?:[.,]\d+)?)", RegexOptions.Compiled);
    private static readonly Regex NumberPattern = new(@"\d+(?:[.,]\d+)?", RegexOptions.Compiled);
    private static readonly Regex RangePattern = new(@"(\d+(?:[.,]\d+)?)\s*[-–—~]\s*(\d+(?:[.,]\d+)?)", RegexOptions.Compiled);

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

        if (correctAnswer == null || string.IsNullOrWhiteSpace(userVal))
            return false;

        var correctText = correctAnswer.Text?.Trim() ?? string.Empty;

        // 1. Приоритет у явного числового значения
        if (correctAnswer.NumericValue.HasValue)
        {
            var userNumbers = ExtractNumbers(userVal);
            return userNumbers.Any(u => Math.Abs(u - correctAnswer.NumericValue.Value) < 0.01);
        }

        var correctNumbers = ExtractNumbers(correctText);
        var userNumbers2 = ExtractNumbers(userVal);

        if (correctNumbers.Count > 0 && userNumbers2.Count > 0)
        {
            // Диапазон в правильном ответе, например "15-25%"
            if (TryParseRange(correctText, out var min, out var max))
                return userNumbers2.Any(u => u >= min - 0.01 && u <= max + 0.01);

            // Совпадение с любым числом из правильного ответа
            return userNumbers2.Any(u => correctNumbers.Any(c => Math.Abs(u - c) < 0.01));
        }

        // 2. Текстовый ответ без чисел (например "on") — сравнение строк
        return string.Equals(NormalizeText(userVal), NormalizeText(correctText), StringComparison.OrdinalIgnoreCase);
    }

    // Извлекает все числа из строки, поддерживая запись степени ("2^32" -> 4294967296)
    private static List<double> ExtractNumbers(string input)
    {
        var result = new List<double>();
        if (string.IsNullOrWhiteSpace(input))
            return result;

        var processed = PowerPattern.Replace(input, m =>
        {
            if (double.TryParse(m.Groups[1].Value.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out var b) &&
                double.TryParse(m.Groups[2].Value.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out var e))
            {
                return Math.Pow(b, e).ToString(CultureInfo.InvariantCulture);
            }
            return m.Value;
        });

        foreach (Match match in NumberPattern.Matches(processed))
        {
            if (double.TryParse(match.Value.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out var val))
                result.Add(val);
        }

        return result;
    }

    private static bool TryParseRange(string text, out double min, out double max)
    {
        min = 0;
        max = 0;

        var match = RangePattern.Match(text);
        if (!match.Success)
            return false;

        if (double.TryParse(match.Groups[1].Value.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out min) &&
            double.TryParse(match.Groups[2].Value.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out max))
        {
            return min <= max;
        }

        min = 0;
        max = 0;
        return false;
    }

    private static string NormalizeText(string value) => value.Replace(",", ".").Trim();

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
