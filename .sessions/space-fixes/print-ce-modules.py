import json
from pathlib import Path

data = json.loads(Path(r"c:\dev\abd-context-driven-delivery\.context\explorer-graph.json").read_text(encoding="utf-8"))
ce = next(g for g in data["practice_graphs"] if g["name"] == "clean_engineering")
mods = sorted(
    (n for n in ce["nodes"] if n.get("semantic_type") == "Module"),
    key=lambda n: n.get("name") or "",
)
print(f"clean_engineering — Practice root children (Module): {len(mods)}")
for n in mods:
    print(f"  Module: {n.get('name')}")

# workspace package roots that own modules
ws = next(g for g in data["practice_graphs"] if g["name"] == "workspace")
print()
print("workspace — Package roots:")
for n in sorted(ws["nodes"], key=lambda x: x.get("name") or ""):
    if n.get("semantic_type") == "Package":
        print(f"  Package: {n.get('name')}")