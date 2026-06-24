using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;

namespace CertifiedTestApplication.Services;

public class UserService : IUserService
{
    private readonly ApplicationDbContext _context;

    public UserService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<User?> GetUserByIdAsync(Guid userId)
    {
        return await _context.Users.FindAsync(userId);
    }

    public async Task<bool> IsUserBlockedAsync(Guid userId)
    {
        var user = await _context.Users.FindAsync(userId);
        return user?.IsBlocked ?? false;
    }

    public async Task<bool> ValidatePasswordAsync(string password, string passwordHash)
    {
        try
        {
            return BCrypt.Net.BCrypt.Verify(password, passwordHash);
        }
        catch
        {
            return false;
        }
    }

    public async Task<string> HashPasswordAsync(string password)
    {
        return await Task.FromResult(BCrypt.Net.BCrypt.HashPassword(password));
    }
}
