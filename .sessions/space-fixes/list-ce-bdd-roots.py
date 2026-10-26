from collections import Counter
from pathlib import Path
import json

from harness.graph.graph import Graph

root = Path(r"c:\dev\abd-context-driven-delivery")
graph = Graph()
message = graph.load_working_copy(
    str(root),
    {
        "clean_engineering": str(root),
        "bdd": str(root),
    },
    force=False,
)
print("msg", message)
print("practices", list(graph.practices))
raw = json.loads(graph.return_nodes({"practices": ["clean_engineering", "bdd"]}))
print("total nodes", len(raw))
print("by practice", dict(Counter(n["practice"] for n in raw)))
for practice in ("clean_engineering", "bdd"):
    tops = [n for n in raw if n.get("ancestors") == [practice]]
    print("---", practice, "roots", len(tops), dict(Counter(n["type"] for n in tops)))
    for node in tops[:40]:
        kids = len(node.get("children") or [])
        print(f"  {node['type']}: {node['name']}  children={kids}")
    if len(tops) > 40:
        print("  ...", len(tops) - 40, "more")
