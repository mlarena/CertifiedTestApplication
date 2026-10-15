"""One-off repair: restore missing opening quote after 'Q(' in generator files."""
import io
import re
import sys

pat = re.compile(r'Q\((?!")')
for path in sys.argv[1:]:
    with io.open(path, encoding="utf-8") as f:
        text = f.read()
    fixed, n = pat.subn('Q("', text)
    if n:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(fixed)
    print("%s: %d fixes" % (path, n))
