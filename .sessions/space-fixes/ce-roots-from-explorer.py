import json
from pathlib import Path

data = json.loads(Path(r"c:\dev\abd-context-driven-delivery\.context\explorer-graph.json").read_text(encoding="utf-8"))
ce = next(g for g in data["practice_graphs"] if g["name"] == "clean_engineering")
nodes = {n["node_id"]: n for n in ce["nodes"]}
owns = [r for r in ce["relationships"] if r.get("kind") == "owns"]
parent_of = {r["to_id"]: r["from_id"] for r in owns}
mods = [n for n in ce["nodes"] if n.get("semantic_type") == "Module"]
top = [
    n
    for n in mods
    if str(parent_of.get(n["node_id"], "")).startswith("pkg:")
    or n["node_id"] not in parent_of
]
print(f"clean_engineering Module roots (under packages): {len(top)}")
for n in sorted(top, key=lambda x: x.get("name") or ""):
    print(f"  Module: {n.get('name')}")
print()
print("bdd practice graph in explorer:", any(g.get("name") == "bdd" for g in data["practice_graphs"]))
print("practice_graphs:", [g.get("name") for g in data["practice_graphs"]])