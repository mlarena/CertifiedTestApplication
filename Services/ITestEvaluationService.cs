using CertifiedTestApplication.Models.Entities;
using CertifiedTestApplication.Models.ViewModels;

namespace CertifiedTestApplication.Services;

public interface ITestEvaluationService
{
    Task<(int CorrectCount, int TotalCount, List<QuestionResultDetail> Results)> EvaluateTestAsync(Guid attemptId);
}
