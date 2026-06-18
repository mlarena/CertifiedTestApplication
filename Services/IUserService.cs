using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Services;

public interface IUserService
{
    Task<User?> GetUserByIdAsync(Guid userId);
    Task<bool> IsUserBlockedAsync(Guid userId);
    Task<bool> ValidatePasswordAsync(string password, string passwordHash);
    Task<string> HashPasswordAsync(string password);
}
