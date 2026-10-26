import json
from collections import Counter
from pathlib import Path

data = json.loads(Path(r"c:\dev\abd-context-driven-delivery\.context\explorer-graph.json").read_text(encoding="utf-8"))
ce = next(g for g in data["practice_graphs"] if g["name"] == "clean_engineering")
nodes = {n["node_id"]: n for n in ce["nodes"]}
owns = [r for r in ce["relationships"] if r.get("kind") == "owns"]
print("owns", len(owns), "nodes", len(nodes))
print("from_id prefixes", Counter(str(r["from_id"]).split(":")[0] for r in owns).most_common(10))
print("to_id prefixes", Counter(str(r["to_id"]).split(":")[0] for r in owns).most_common(10))
print("semantic types", Counter(n.get("semantic_type") for n in ce["nodes"]).most_common(15))
# Module nodes and their parents
mods = [n for n in ce["nodes"] if n.get("semantic_type") == "Module"]
print("modules", len(mods))
parent_of = {r["to_id"]: r["from_id"] for r in owns}
parent_types = Counter()
for n in mods:
    pid = parent_of.get(n["node_id"])
    if pid is None:
        parent_types["<none>"] += 1
    else:
        p = nodes.get(pid)
        parent_types[(p.get("semantic_type") if p else "?") + "/" + str(pid).split(":")[0]] += 1
print("module parents", parent_types.most_common(20))
# Print modules with no parent or package parent
for n in sorted(mods, key=lambda x: x["name"])[:5]:
    print("sample mod", n["name"], "parent", parent_of.get(n["node_id"]))
# package -> module edges from workspace graph
ws = next(g for g in data["practice_graphs"] if g["name"] == "workspace")
ws_owns = [r for r in ws.get("relationships") or [] if r.get("kind") == "owns"]
print("workspace owns", len(ws_owns))
for r in ws_owns[:20]:
    to = nodes.get(r["to_id"]) or {}
    print(" ", r["from_id"], "->", to.get("semantic_type"), to.get("name"), r["to_id"][:60])