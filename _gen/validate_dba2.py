"""Validate all DBA2 topic test files in json/: structure, types, duplicates."""
import glob
import io
import json
import os

files = sorted(glob.glob(os.path.join("json", "DBA2_*.json")))
print("found %d DBA2 files" % len(files))

all_texts = {}
total = 0
type_stats = {}
problems_all = []

for path in files:
    problems = []
    try:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print("ERROR %s: %s" % (path, exc))
        problems_all.append(path)
        continue

    if not data.get("Title"):
        problems.append("empty Title")
    if not data.get("Description"):
        problems.append("empty Description")

    questions = data.get("Questions", [])
    total += len(questions)
    if len(questions) != 15:
        problems.append("expected 15 questions, got %d" % len(questions))

    for i, q in enumerate(questions, 1):
        t = q.get("Type")
        answers = q.get("Answers", [])
        correct = [a for a in answers if a.get("IsCorrect")]
        type_stats[t] = type_stats.get(t, 0) + 1

        if not q.get("Text"):
            problems.append("Q%d: empty text" % i)
        if q.get("Order") != i:
            problems.append("Q%d: bad Order %s" % (i, q.get("Order")))
        if len(answers) < 2:
            problems.append("Q%d: only %d answers" % (i, len(answers)))
        if len(set(a["Text"] for a in answers)) != len(answers):
            problems.append("Q%d: duplicate answer texts" % i)
        if not correct:
            problems.append("Q%d: no correct answer" % i)
        if t == 1 and len(correct) != 1:
            problems.append("Q%d: Single with %d correct" % (i, len(correct)))
        if t == 2 and len(correct) < 2:
            problems.append("Q%d: Multiple with %d correct" % (i, len(correct)))
        if t == 3:
            if len(correct) != 1:
                problems.append("Q%d: Numeric needs exactly 1 correct" % i)
            elif correct[0].get("NumericValue") is None:
                problems.append("Q%d: Numeric answer without NumericValue" % i)
        for a in answers:
            if "IsCorrect" not in a or "Text" not in a:
                problems.append("Q%d: malformed answer" % i)

        key = q.get("Text", "").strip().lower()
        if key in all_texts:
            problems.append("Q%d: duplicate text, also in %s" % (i, all_texts[key]))
        else:
            all_texts[key] = os.path.basename(path)

    name = os.path.basename(path)
    if problems:
        problems_all.append(name)
    print("%-52s %2d q  problems: %s"
          % (name, len(questions), "; ".join(problems) or "NONE"))

# Cross-check against every other test file in json/
print("\nchecking duplicates against all other json/ files...")
collisions = 0
for path in sorted(glob.glob(os.path.join("json", "*.json"))):
    if os.path.basename(path).startswith("DBA2_"):
        continue
    try:
        with io.open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        continue
    for q in data.get("Questions", []):
        key = q.get("Text", "").strip().lower()
        if key in all_texts:
            collisions += 1
            print("  DUP: %s  [%s vs %s]"
                  % (q.get("Text", "")[:60], os.path.basename(path),
                     all_texts[key]))

print("\ntotal DBA2 questions: %d" % total)
print("type stats (1=Single, 2=Multiple, 3=Numeric): %s" % type_stats)
print("files with problems: %s" % (problems_all or "NONE"))
print("cross-file duplicates: %d" % collisions)
