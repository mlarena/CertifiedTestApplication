using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Models.ViewModels;

public class QuestionResultViewModel
{
    public Question Question { get; set; } = null!;
    public List<Answer> Answers { get; set; } = null!;
    public List<UserAnswer> UserAnswers { get; set; } = null!;
    public bool IsCorrect { get; set; }
}
