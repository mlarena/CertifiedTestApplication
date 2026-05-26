using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Models.DTO;

public class TestExportDto
{
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public int TimeLimit { get; set; }
    public bool CanReturnToQuestion { get; set; }
    public List<QuestionExportDto> Questions { get; set; } = new();
}

public class QuestionExportDto
{
    public string Text { get; set; } = string.Empty;
    public QuestionType Type { get; set; }
    public int Order { get; set; }
    public List<AnswerExportDto> Answers { get; set; } = new();
}

public class AnswerExportDto
{
    public string Text { get; set; } = string.Empty;
    public bool IsCorrect { get; set; }
    public double? NumericValue { get; set; }
}
