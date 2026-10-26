import json
from collections import Counter
from pathlib import Path

path = Path(r"c:\dev\abd-context-driven-delivery\.context\graph.json")
data = json.loads(path.read_text(encoding="utf-8"))
practices = data.get("practices") or {}
print("practices", list(practices))
for name, row in practices.items():
    nodes = row.get("nodes") or []
    print(f"=== {name} source_root={row.get('source_root')} nodes={len(nodes)}")
    # nodes are list rows in save format: [id, name, type, ...] from _node_row
    # check first row shape
    if nodes:
        print("  sample row", nodes[0][:8] if isinstance(nodes[0], list) else list(nodes[0])[:8] if isinstance(nodes[0], dict) else nodes[0])
    types = Counter()
    for n in nodes:
        if isinstance(n, list) and len(n) >= 3:
            types[n[2]] += 1
        elif isinstance(n, dict):
            types[n.get("type") or n.get("semantic_type")] += 1
    print("  types", dict(types.most_common(12)))