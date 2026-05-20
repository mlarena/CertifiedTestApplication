using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using Microsoft.AspNetCore.Authorization;

namespace CertifiedTestApplication.Controllers;

[Authorize(Roles = "Admin")]
public class CategoriesController : Controller
{
    private readonly ApplicationDbContext _context;

    public CategoriesController(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<IActionResult> Index()
    {
        var categories = await _context.Categories
            .Select(c => new {
                Category = c,
                TestsCount = _context.Tests.Count(t => t.CategoryId == c.Id)
            })
            .ToListAsync();
            
        return View(categories);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(string name)
    {
        if (!string.IsNullOrWhiteSpace(name))
        {
            var category = new Category { Name = name.Trim() };
            _context.Categories.Add(category);
            
            _context.Logs.Add(new Log { 
                Action = "Создание категории", 
                EntityName = "Category", 
                EntityId = name,
                UserId = Guid.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value)
            });

            await _context.SaveChangesAsync();
        }
        return RedirectToAction(nameof(Index));
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int id)
    {
        var hasTests = await _context.Tests.AnyAsync(t => t.CategoryId == id);
        if (hasTests)
        {
            TempData["Error"] = "Нельзя удалить категорию, в которой есть тесты.";
            return RedirectToAction(nameof(Index));
        }

        var category = await _context.Categories.FindAsync(id);
        if (category != null)
        {
            _context.Categories.Remove(category);
            
            _context.Logs.Add(new Log { 
                Action = "Удаление категории", 
                EntityName = "Category", 
                EntityId = category.Name,
                UserId = Guid.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value)
            });

            await _context.SaveChangesAsync();
        }
        return RedirectToAction(nameof(Index));
    }
}
