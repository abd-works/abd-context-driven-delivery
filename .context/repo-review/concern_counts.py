"""Count a validation round's findings by concern: python concern_counts.py round6-*.md. Each table row counts once per concern it names."""
import re,glob,sys
files=sys.argv[1:]
tot={}; rows=0
for f in files:
    ci=None
    for l in open(f,encoding='utf-8'):
        if not l.startswith('|'): ci=None if not l.strip() else ci; continue
        cells=[x.strip() for x in l.strip().strip('|').split('|')]
        low=[c.lower() for c in cells]
        if 'concern' in low: ci=low.index('concern'); continue
        if ci is None or set(l.strip())<=set('|- '): continue
        if ci>=len(cells): continue
        ks=set(int(k) for k in re.findall(r'\b(1[0-2]|[1-9])\b',cells[ci]))
        rows+=1
        for k in ks: tot[k]=tot.get(k,0)+1
print('rows',rows,dict(sorted(tot.items())))
