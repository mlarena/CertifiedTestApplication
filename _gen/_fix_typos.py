"""One-off repair: fix 'A="' -> 'A("' and 'Q="' -> 'Q(' typos in generator files."""
import io
import sys

for path in sys.argv[1:]:
    with io.open(path, encoding="utf-8") as f:
        text = f.read()
    fixed = text.replace('A="', 'A("').replace('Q="', 'Q(')
    if fixed != text:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(fixed)
        print("repaired %s" % path)
    else:
        print("unchanged %s" % path)
