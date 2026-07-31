path = r'c:\dev\abd-works-repo\abd-context-driven-delivery\context_tools\cdd\cdd.py'
content = open(path, 'r', encoding='utf-8').read()

old = '''    "spec": [
        (Stories, "specification"),
        (Ux, "specification"),
    ],'''

new = '''    "spec": [
        (Ddd, "code"),
        (Stories, "specification"),
        (Ux, "specification"),
        (CleanEngineering, "code"),   # "specification" fidelity removed; Phase 1 typed contracts are now part of "code"
        (Bdd, "development"),
    ],'''

if old in content:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print('spec block restored OK')
else:
    print('NOT FOUND')
    idx = content.find('"spec"')
    print(repr(content[idx:idx+200]))
