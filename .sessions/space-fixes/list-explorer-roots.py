import json
from collections import Counter
from pathlib import Path

data = json.loads(Path(r"c:\dev\abd-context-driven-delivery\.context\explorer-graph.json").read_text(encoding="utf-8"))
for g in data.get("practice_graphs") or []:
    name = g.get("name")
    nodes = g.get("nodes") or []
    rels = g.get("relationships") or []
    child_ids = {r["to_id"] for r in rels if r.get("kind") == "owns"}
    roots = [n for n in nodes if n.get("node_id") not in child_ids]
    # Prefer Module-type roots for CE; for bdd look for Spec-ish
    print("===", name, "nodes", len(nodes), "unowned-roots", len(roots))
    by = Counter(n.get("semantic_type") for n in roots)
    print("  root types", dict(by))
    # top package/module roots (not Parameters)
    interesting = [n for n in roots if n.get("semantic_type") in {"Module", "Package", "Spec", "Describe", "Context", "File"}]
    print("  interesting roots", len(interesting))
    for n in interesting[:25]:
        print(f"    {n.get('semantic_type')}: {n.get('name')}")
    if len(interesting) > 25:
        print("   ...", len(interesting)-25, "more")
