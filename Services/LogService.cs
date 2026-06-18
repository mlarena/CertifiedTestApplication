using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Services;

public class LogService : ILogService
{
    private readonly ApplicationDbContext _context;

    public LogService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task LogActionAsync(string action, string? entityName = null, string? entityId = null, Guid? userId = null, string? ipAddress = null)
    {
        _context.Logs.Add(new Log
        {
            Action = action,
            EntityName = entityName,
            EntityId = entityId,
            UserId = userId,
            IPAddress = ipAddress,
            Timestamp = DateTime.UtcNow
        });

        await _context.SaveChangesAsync();
    }
}
