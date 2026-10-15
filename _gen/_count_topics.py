"""Count questions per topic section in DBA2 generator files."""
import io
import re
import sys

topic_pat = re.compile(r'# Topic (\d+)')
q_pat = re.compile(r'Qs\.append\(QN?\(')

for path in sys.argv[1:]:
    with io.open(path, encoding="utf-8") as f:
        lines = f.readlines()
    current = None
    counts = {}
    for line in lines:
        m = topic_pat.search(line)
        if m:
            current = m.group(1)
            counts.setdefault(current, 0)
            continue
        if current and q_pat.search(line):
            counts[current] += 1
    print(path)
    for k in sorted(counts):
        flag = "" if counts[k] == 15 else "  <-- expected 15"
        print("  topic %s: %d%s" % (k, counts[k], flag))
