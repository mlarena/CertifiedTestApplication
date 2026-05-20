using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using Microsoft.AspNetCore.Authorization;

namespace CertifiedTestApplication.Controllers;

[Authorize(Roles = "Admin")]
public class UsersController : Controller
{
    private readonly ApplicationDbContext _context;

    public UsersController(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<IActionResult> Index()
    {
        var users = await _context.Users.Include(u => u.Role).ToListAsync();
        return View(users);
    }

    [HttpGet]
    public async Task<IActionResult> Create()
    {
        ViewBag.Roles = await _context.Roles.ToListAsync();
        return View();
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(User user, string password)
    {
        if (await _context.Users.AnyAsync(u => u.Login == user.Login))
        {
            ModelState.AddModelError("Login", "Такой логин уже занят");
        }

        if (ModelState.IsValid)
        {
            user.Id = Guid.NewGuid();
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(password);
            user.CreatedAt = DateTime.UtcNow;
            
            _context.Add(user);
            
            // Логирование
            _context.Logs.Add(new Log { 
                Action = "Создание пользователя", 
                EntityName = "User", 
                EntityId = user.Id.ToString(),
                UserId = Guid.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value),
                Timestamp = DateTime.UtcNow
            });

            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }
        ViewBag.Roles = await _context.Roles.ToListAsync();
        return View(user);
    }

    [HttpPost]
    public async Task<IActionResult> ToggleBlock(Guid id)
    {
        var user = await _context.Users.FindAsync(id);
        if (user != null && user.Login != "sa")
        {
            user.IsBlocked = !user.IsBlocked;
            
            _context.Logs.Add(new Log { 
                Action = user.IsBlocked ? "Блокировка пользователя" : "Разблокировка пользователя", 
                EntityName = "User", 
                EntityId = user.Id.ToString(),
                UserId = Guid.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value),
                Timestamp = DateTime.UtcNow
            });

            await _context.SaveChangesAsync();
        }
        return RedirectToAction(nameof(Index));
    }
}
