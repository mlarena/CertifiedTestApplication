import glob, io, json
out = []
for p in sorted(glob.glob('json/*.json')):
    try:
        d = json.loads(io.open(p, encoding='utf-8-sig').read())
    except Exception as e:
        out.append('PARSE_FAIL %s %s' % (p, e)); continue
    for q in d.get('Questions', []):
        out.append(q.get('Text', '').strip())
io.open('_existing_questions.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('unique questions:', len(set(out)), '| total:', len(out))
