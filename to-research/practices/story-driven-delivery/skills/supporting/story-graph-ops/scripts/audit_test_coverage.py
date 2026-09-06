"""
Audit story-graph.json for test coverage.
Prints a table of every story with test_files / scenarios / ACs counts,
then summarises missing entries.
"""
import json, sys

GRAPH = r"C:\dev\paradise-mobile\pml-my\docs\stories\story-graph.json"

data = json.load(open(GRAPH, encoding="utf-8"))

def iter_stories(node):
    """Recursively yield (epic_chain, story) tuples."""
    if isinstance(node, dict):
        if "story_type" in node:
            yield node
        for key in ("epics", "sub_epics", "story_groups", "stories"):
            for child in node.get(key, []):
                yield from iter_stories(child)
    elif isinstance(node, list):
        for item in node:
            yield from iter_stories(item)

stories = list(iter_stories(data))

PASS = "\u2713"
FAIL = "\u2717"

rows = []
for s in stories:
    name  = s.get("name", "?")[:55]
    tfs   = s.get("test_files", [])
    scens = s.get("scenarios", [])
    acs   = s.get("acceptance_criteria", [])
    rows.append((name, len(tfs), len(scens), len(acs)))

# Header
print(f"{'Story':<56} {'TF':>3} {'SC':>3} {'AC':>3}  {'OK?'}")
print("-" * 72)

missing = []
for name, tf, sc, ac in rows:
    ok = tf > 0 and sc > 0 and ac > 0
    flag = PASS if ok else FAIL
    print(f"{name:<56} {tf:>3} {sc:>3} {ac:>3}  {flag}")
    if not ok:
        issues = []
        if tf == 0: issues.append("no test_files")
        if sc == 0: issues.append("no scenarios")
        if ac == 0: issues.append("no ACs")
        missing.append((name, issues))

print("-" * 72)
print(f"Total: {len(rows)} stories  |  Missing coverage: {len(missing)}")

if missing:
    print("\nStories with gaps:")
    for name, issues in missing:
        print(f"  {FAIL} {name} -> {', '.join(issues)}")
else:
    print("\nAll stories have test_files, scenarios, and acceptance_criteria.")
