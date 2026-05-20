using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using Microsoft.AspNetCore.Authorization;

namespace CertifiedTestApplication.Controllers;

[Authorize(Roles = "Admin,Engineer")]
public class TestsController : Controller
{
    private readonly ApplicationDbContext _context;
    private readonly IWebHostEnvironment _environment;

    public TestsController(ApplicationDbContext context, IWebHostEnvironment environment)
    {
        _context = context;
        _environment = environment;
    }

    // Список тестов
    public async Task<IActionResult> Index()
    {
        var tests = await _context.Tests
            .Include(t => t.Category)
            .Include(t => t.Author)
            .ToListAsync();
        return View(tests);
    }

    // Создание теста
    [HttpGet]
    public async Task<IActionResult> Create()
    {
        ViewBag.Categories = await _context.Categories.ToListAsync();
        return View();
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(Test test)
    {
        if (ModelState.IsValid)
        {
            test.Id = Guid.NewGuid();
            test.AuthorId = Guid.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value);
            _context.Add(test);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Edit), new { id = test.Id });
        }
        ViewBag.Categories = await _context.Categories.ToListAsync();
        return View(test);
    }

    // Редактирование заголовка теста
    [HttpGet]
    public async Task<IActionResult> Edit(Guid id)
    {
        var test = await _context.Tests
            .Include(t => t.Category)
            .FirstOrDefaultAsync(t => t.Id == id);
            
        if (test == null) return NotFound();

        ViewBag.Categories = await _context.Categories.ToListAsync();
        ViewBag.Questions = await _context.Questions
            .Where(q => q.TestId == id)
            .OrderBy(q => q.Order)
            .ToListAsync();

        return View(test);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(Test test)
    {
        if (ModelState.IsValid)
        {
            _context.Update(test);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }
        ViewBag.Categories = await _context.Categories.ToListAsync();
        return View(test);
    }

    // --- Управление вопросами ---

    [HttpGet]
    public IActionResult AddQuestion(Guid testId)
    {
        var question = new Question { TestId = testId, Order = 0 };
        return View(question);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AddQuestion(Question question, IFormFile? image)
    {
        if (ModelState.IsValid)
        {
            question.Id = Guid.NewGuid();
            
            if (image != null)
            {
                string uploadsFolder = Path.Combine(_environment.WebRootPath, "uploads", "questions");
                if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);
                
                string uniqueFileName = Guid.NewGuid().ToString() + "_" + image.FileName;
                string filePath = Path.Combine(uploadsFolder, uniqueFileName);
                using (var fileStream = new FileStream(filePath, FileMode.Create))
                {
                    await image.CopyToAsync(fileStream);
                }
                question.ImagePath = "/uploads/questions/" + uniqueFileName;
            }

            _context.Add(question);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(EditQuestion), new { id = question.Id });
        }
        return View(question);
    }

    [HttpGet]
    public async Task<IActionResult> EditQuestion(Guid id)
    {
        var question = await _context.Questions
            .Include(q => q.Test)
            .FirstOrDefaultAsync(q => q.Id == id);
            
        if (question == null) return NotFound();

        ViewBag.Answers = await _context.Answers
            .Where(a => a.QuestionId == id)
            .ToListAsync();

        return View(question);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditQuestion(Question question, IFormFile? image)
    {
        if (ModelState.IsValid)
        {
            if (image != null)
            {
                string uploadsFolder = Path.Combine(_environment.WebRootPath, "uploads", "questions");
                string uniqueFileName = Guid.NewGuid().ToString() + "_" + image.FileName;
                string filePath = Path.Combine(uploadsFolder, uniqueFileName);
                using (var fileStream = new FileStream(filePath, FileMode.Create))
                {
                    await image.CopyToAsync(fileStream);
                }
                question.ImagePath = "/uploads/questions/" + uniqueFileName;
            }

            _context.Update(question);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Edit), new { id = question.TestId });
        }
        return View(question);
    }

    [HttpPost]
    public async Task<IActionResult> DeleteQuestion(Guid id)
    {
        var question = await _context.Questions.FindAsync(id);
        if (question != null)
        {
            var testId = question.TestId;
            _context.Questions.Remove(question);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Edit), new { id = testId });
        }
        return RedirectToAction(nameof(Index));
    }

    // --- Управление ответами ---

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AddAnswer(Guid questionId, string text, bool isCorrect, double? numericValue)
    {
        var answer = new Answer
        {
            Id = Guid.NewGuid(),
            QuestionId = questionId,
            Text = text,
            IsCorrect = isCorrect,
            NumericValue = numericValue
        };
        _context.Answers.Add(answer);
        await _context.SaveChangesAsync();
        return RedirectToAction(nameof(EditQuestion), new { id = questionId });
    }

    [HttpPost]
    public async Task<IActionResult> DeleteAnswer(Guid id)
    {
        var answer = await _context.Answers.FindAsync(id);
        if (answer != null)
        {
            var qId = answer.QuestionId;
            _context.Answers.Remove(answer);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(EditQuestion), new { id = qId });
        }
        return RedirectToAction(nameof(Index));
    }
}
