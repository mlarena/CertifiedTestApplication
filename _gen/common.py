"""Shared helpers for JSON test generators."""
import json
import random


def A(text, ok=True, nv=None):
    """Answer helper: A("text", True) or A("text", False)."""
    return {"Text": text, "IsCorrect": bool(ok), "NumericValue": nv}


def Q(text, answers, order=1, qtype=None):
    """Question helper. qtype: None=auto (1 single / 2 multiple), 1, 2, 3."""
    correct = sum(1 for a in answers if a["IsCorrect"])
    if qtype is None:
        qtype = 2 if correct > 1 else 1
    return {"Text": text, "Type": qtype, "Order": order, "Answers": answers}


def QN(text, correct, order=1, distractors=()):
    """Numeric question helper: correct answer carries NumericValue."""
    answers = [A(str(correct), True, float(correct))]
    for d in distractors:
        answers.append(A(str(d), False, None))
    return {"Text": text, "Type": 3, "Order": order, "Answers": answers}


def dump_json(title, desc, questions, path, time_limit=1200):
    """Deterministically shuffle answers and write the test JSON file."""
    for idx, q in enumerate(questions):
        q["Order"] = idx + 1
        rnd = random.Random(hash(title) ^ (idx * 7919 + 13))
        rnd.shuffle(q["Answers"])
    data = {
        "Title": title,
        "Description": desc,
        "TimeLimit": time_limit,
        "CanReturnToQuestion": True,
        "Questions": questions,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d questions -> %s" % (len(questions), path))
