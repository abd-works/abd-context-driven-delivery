"""Load the whole working copy for all five practices and write every invokes edge, one per line."""
import json, sys, tempfile, time
from pathlib import Path
repo = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2])
sys.path.insert(0, str(repo))
from harness.graph.graph import Graph
import cdd_guidance.practices  # noqa: F401
db = Path(tempfile.mkdtemp())
started = time.time()
graph = Graph()
graph.load_working_copy(str(repo), {k: "." for k in ("stories", "ddd", "ux", "clean_engineering", "bdd")}, force=True)
lines = []
for key in ("stories", "ddd", "ux", "clean_engineering", "bdd"):
    practice = graph.practices.named(key)
    for edge in practice.reading.in_graph.edge_index.of("invokes"):
        facts = ",".join(sorted(v for vals in (edge.facts or {}).values() for v in vals))
        lines.append(f"{key}\t{edge.parent.node_id}\t{edge.child.node_id}\t{facts}")
out.write_text("\n".join(sorted(lines)), encoding="utf-8")
print(len(lines), "invokes edges in", round(time.time() - started), "s")
