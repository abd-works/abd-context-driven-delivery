"""Load the whole working copy of a checkout for all five practices, with the LERN overlay applied so its schema keys
and kinds are read too, and write the saved graph document, sorted, to compare node types, edge kinds, edge order and
inverse edges before and after a change. python -I graph_json_dump.py <checkout> <out.json>"""
import json, sys, time
from pathlib import Path
repo = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2])
sys.path.insert(0, str(repo))
from harness.graph.graph import Graph
from harness.graph.saved_graph import SavedGraph
import cdd_guidance.practices  # noqa: F401
import cdd_guidance.patterns  # noqa: F401
started = time.time()
graph = Graph()
graph.load_working_copy(str(repo), {k: "." for k in ("stories", "ddd", "ux", "clean_engineering", "bdd")}, force=True)
document = SavedGraph.from_graph(graph).document
out.write_text(json.dumps(document, sort_keys=True, indent=0), encoding="utf-8")
print("saved in", round(time.time() - started), "s")
