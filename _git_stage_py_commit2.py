#!/usr/bin/env python3
\"\"\"Stage modified .py files and commit with a standardized message.\"\"\"
import subprocess
import sys

def run(cmd):
    return subprocess.run(cmd, check=False, capture_output=True, text=True)

p = run(['git', 'status', '--porcelain=v1'])
lines = [l for l in p.stdout.splitlines() if l.strip()]
py_files = []
for l in lines:
    parts = l.split(None, 1)
    if len(parts) < 2:
        continue
    path = parts[1]
    if path.endswith('.py'):
        py_files.append(path)

if not py_files:
    print('No modified .py files to add.')
    sys.exit(0)

print(f'Adding {len(py_files)} .py files to index...')
rc = run(['git', 'add'] + py_files)
if rc.returncode != 0:
    print('git add failed:', rc.stderr)
    sys.exit(rc.returncode)

msg = 'ci: replace non-ASCII in .py files to avoid Windows console encoding errors'
rc = run(['git', 'commit', '-m', msg])
if rc.returncode != 0:
    print('git commit failed:', rc.stderr)
    sys.exit(rc.returncode)

print('Committed:')
print(run(['git', 'log', '-1', '--pretty=format:%H %s']).stdout)

