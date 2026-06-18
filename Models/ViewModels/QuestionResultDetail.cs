using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Models.ViewModels;

public class QuestionResultDetail
{
    public Question Question { get; set; } = null!;
    public bool IsCorrect { get; set; }
    public List<UserAnswer> UserAnswers { get; set; } = null!;
    public List<Answer> CorrectAnswers { get; set; } = null!;
    public List<Answer> AllAnswers { get; set; } = null!;
}
