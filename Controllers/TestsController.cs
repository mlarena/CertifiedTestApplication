using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CertifiedTestApplication.Data;
using CertifiedTestApplication.Models.Entities;
using CertifiedTestApplication.Models.DTO;
using Microsoft.AspNetCore.Authorization;
using Newtonsoft.Json;
using System.Text;

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

    // --- Экспорт и Импорт ---

    public async Task<IActionResult> Export(Guid id)
    {
        var test = await _context.Tests
            .Include(t => t.Category)
            .FirstOrDefaultAsync(t => t.Id == id);

        if (test == null) return NotFound();

        var questions = await _context.Questions
            .Where(q => q.TestId == id)
            .OrderBy(q => q.Order)
            .ToListAsync();

        var exportDto = new TestExportDto
        {
            Title = test.Title,
            Description = test.Description,
            TimeLimit = test.TimeLimit,
            CanReturnToQuestion = test.CanReturnToQuestion,
            Questions = new List<QuestionExportDto>()
        };

        foreach (var q in questions)
        {
            var answers = await _context.Answers
                .Where(a => a.QuestionId == q.Id)
                .ToListAsync();

            exportDto.Questions.Add(new QuestionExportDto
            {
                Text = q.Text,
                Type = q.Type,
                Order = q.Order,
                Answers = answers.Select(a => new AnswerExportDto
                {
                    Text = a.Text,
                    IsCorrect = a.IsCorrect,
                    NumericValue = a.NumericValue
                }).ToList()
            });
        }

        var json = JsonConvert.SerializeObject(exportDto, Formatting.Indented);
        var fileName = $"Test_{test.Title.Replace(" ", "_")}.json";
        return File(Encoding.UTF8.GetBytes(json), "application/json", fileName);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Import(IFormFile jsonFile, int categoryId)
    {
        if (jsonFile == null || jsonFile.Length == 0)
        {
            TempData["Error"] = "Файл не выбран";
            return RedirectToAction(nameof(Index));
        }

        try
        {
            using var reader = new StreamReader(jsonFile.OpenReadStream());
            var content = await reader.ReadToEndAsync();
            var importDto = JsonConvert.DeserializeObject<TestExportDto>(content);

            if (importDto == null) throw new Exception("Неверный формат файла");

            var test = new Test
            {
                Id = Guid.NewGuid(),
                Title = importDto.Title + " (Импорт)",
                Description = importDto.Description,
                TimeLimit = importDto.TimeLimit,
                CanReturnToQuestion = importDto.CanReturnToQuestion,
                CategoryId = categoryId,
                AuthorId = Guid.Parse(User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value),
                IsActive = false
            };

            _context.Tests.Add(test);

            foreach (var qDto in importDto.Questions)
            {
                var question = new Question
                {
                    Id = Guid.NewGuid(),
                    TestId = test.Id,
                    Text = qDto.Text,
                    Type = qDto.Type,
                    Order = qDto.Order
                };
                _context.Questions.Add(question);

                foreach (var aDto in qDto.Answers)
                {
                    _context.Answers.Add(new Answer
                    {
                        Id = Guid.NewGuid(),
                        QuestionId = question.Id,
                        Text = aDto.Text,
                        IsCorrect = aDto.IsCorrect,
                        NumericValue = aDto.NumericValue
                    });
                }
            }

            await _context.SaveChangesAsync();
            TempData["Success"] = $"Тест '{test.Title}' успешно импортирован";
        }
        catch (Exception ex)
        {
            TempData["Error"] = "Ошибка при импорте: " + ex.Message;
        }

        return RedirectToAction(nameof(Index));
    }

    // Список тестов
    public async Task<IActionResult> Index()
    {
        ViewBag.Categories = await _context.Categories.ToListAsync();
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
        var questions = await _context.Questions
            .Where(q => q.TestId == id)
            .OrderBy(q => q.Order)
            .ToListAsync();

        foreach (var q in questions)
        {
            q.Answers = await _context.Answers
                .Where(a => a.QuestionId == q.Id)
                .ToListAsync();
        }

        ViewBag.Questions = questions;
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
    public async Task<IActionResult> AddQuestion(Guid testId)
    {
        var maxOrder = await _context.Questions
            .Where(q => q.TestId == testId)
            .MaxAsync(q => (int?)q.Order) ?? 0;

        var question = new Question { TestId = testId, Order = maxOrder + 1 };
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
            .OrderBy(a => a.Text)
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
                if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);

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
            TempData["Success"] = "Вопрос сохранён";
            return RedirectToAction(nameof(EditQuestion), new { id = question.Id });
        }

        ViewBag.Answers = await _context.Answers
            .Where(a => a.QuestionId == question.Id)
            .ToListAsync();

        return View(question);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DeleteQuestion(Guid id)
    {
        var question = await _context.Questions.FindAsync(id);
        if (question != null)
        {
            var testId = question.TestId;
            _context.Questions.Remove(question);
            await _context.SaveChangesAsync();
            TempData["Success"] = "Вопрос удалён";
            return RedirectToAction(nameof(Edit), new { id = testId });
        }
        return RedirectToAction(nameof(Index));
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> UpdateQuestionOrder(Guid testId, Guid[] questionIds)
    {
        for (int i = 0; i < questionIds.Length; i++)
        {
            var question = await _context.Questions.FindAsync(questionIds[i]);
            if (question != null && question.TestId == testId)
            {
                question.Order = i + 1;
            }
        }
        await _context.SaveChangesAsync();
        return Ok();
    }

    // --- Управление ответами ---

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AddAnswer(Guid questionId, string text, bool isCorrect, double? numericValue)
    {
        var question = await _context.Questions.FindAsync(questionId);
        if (question == null) return NotFound();

        if (string.IsNullOrWhiteSpace(text))
        {
            TempData["Error"] = "Текст ответа не может быть пустым";
            return RedirectToAction(nameof(EditQuestion), new { id = questionId });
        }

        var answer = new Answer
        {
            Id = Guid.NewGuid(),
            QuestionId = questionId,
            Text = text.Trim(),
            IsCorrect = isCorrect,
            NumericValue = question.Type == QuestionType.Numeric ? numericValue : null
        };

        _context.Answers.Add(answer);
        await _context.SaveChangesAsync();
        TempData["Success"] = "Ответ добавлен";
        return RedirectToAction(nameof(EditQuestion), new { id = questionId });
    }

    [HttpGet]
    public async Task<IActionResult> EditAnswer(Guid id)
    {
        var answer = await _context.Answers
            .Include(a => a.Question)
            .FirstOrDefaultAsync(a => a.Id == id);

        if (answer == null) return NotFound();

        return View(answer);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditAnswer(Answer answer)
    {
        var existing = await _context.Answers.FindAsync(answer.Id);
        if (existing == null) return NotFound();

        if (string.IsNullOrWhiteSpace(answer.Text))
        {
            TempData["Error"] = "Текст ответа не может быть пустым";
            return RedirectToAction(nameof(EditQuestion), new { id = existing.QuestionId });
        }

        existing.Text = answer.Text.Trim();
        existing.IsCorrect = answer.IsCorrect;
        existing.NumericValue = answer.NumericValue;

        await _context.SaveChangesAsync();
        TempData["Success"] = "Ответ сохранён";
        return RedirectToAction(nameof(EditQuestion), new { id = existing.QuestionId });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ToggleAnswerCorrect(Guid id)
    {
        var answer = await _context.Answers.FindAsync(id);
        if (answer == null) return NotFound();

        answer.IsCorrect = !answer.IsCorrect;
        await _context.SaveChangesAsync();

        return RedirectToAction(nameof(EditQuestion), new { id = answer.QuestionId });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DeleteAnswer(Guid id)
    {
        var answer = await _context.Answers.FindAsync(id);
        if (answer != null)
        {
            var qId = answer.QuestionId;
            _context.Answers.Remove(answer);
            await _context.SaveChangesAsync();
            TempData["Success"] = "Ответ удалён";
            return RedirectToAction(nameof(EditQuestion), new { id = qId });
        }
        return RedirectToAction(nameof(Index));
    }

    [HttpPost]
    public async Task<IActionResult> SaveAnswerInline(Guid id, string text, bool isCorrect)
    {
        var answer = await _context.Answers.FindAsync(id);
        if (answer == null) return NotFound();

        answer.Text = text?.Trim() ?? "";
        answer.IsCorrect = isCorrect;

        await _context.SaveChangesAsync();
        return Ok();
    }
}
