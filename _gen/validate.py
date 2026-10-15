import json
import os

files = ['General_Junior.json', 'General_Middle.json', 'General_Senior.json', 'General_Master.json']
for f in files:
    p = os.path.join('json', f)
    try:
        with open(p, encoding='utf-8') as fh:
            d = json.load(fh)
        types = {}
        problems = []
        for i, q in enumerate(d['Questions'], 1):
            t = q['Type']
            types[t] = types.get(t, 0) + 1
            correct = sum(1 for a in q['Answers'] if a['IsCorrect'])
            if correct == 0:
                problems.append("Q%d has no correct answer" % i)
            if t == 1 and correct > 1:
                problems.append("Q%d is Single but has %d correct" % (i, correct))
            if t == 2 and correct < 2:
                problems.append("Q%d is Multiple but has %d correct" % (i, correct))
            if len(q['Answers']) < 2:
                problems.append("Q%d has only %d answers" % (i, len(q['Answers'])))
        print("%s: %d questions, types=%s, problems=%s" % (f, len(d['Questions']), types, problems or 'NONE'))
    except Exception as e:
        print("ERROR %s: %s" % (f, e))
