from pathlib import Path
root = Path(r'c:\dev\abd-works-repo\abd-context-driven-delivery\context_tools\cdd')
files = list(root.rglob('*'))
total = 0
for p in sorted(files):
    if p.is_file():
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        bad = []
        for lineno, line in enumerate(text.splitlines(), 1):
            for ch in line:
                if ord(ch) > 127:
                    bad.append((lineno, ch, hex(ord(ch))))
        if bad:
            print(str(p.relative_to(root)), 'count', len(bad))
            for b in bad[:200]:
                print(' ', b)
            total += len(bad)
print('TOTAL', total)
