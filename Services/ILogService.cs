using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Services;

public interface ILogService
{
    Task LogActionAsync(string action, string? entityName = null, string? entityId = null, Guid? userId = null, string? ipAddress = null);
}
