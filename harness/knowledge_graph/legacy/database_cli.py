"""Run KnowledgeGraph database operations for the explorer."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_HARNESS = (_REPO / "harness").resolve()
sys.path[:] = [
    item
    for item in sys.path
    if not item or Path(item).resolve() != _HARNESS
]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
try:
    import mcp.types  # SDK; harness/mcp must not shadow this
except ModuleNotFoundError:
    pass
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) < 2:
        raise SystemExit("usage: database_cli.py create-database|refresh-master|reload-working-copy ROOT")
    operation, root = args[0], Path(args[1])
    graph = KnowledgeGraph()
    graph.folder = root
    if operation == "create-database":
        graph.createDatabase()
        return
    if operation == "refresh-master":
        graph.copyWorkingCopyToMaster()
        return
    if operation == "reload-working-copy":
        graph.copyMasterToWorkingCopy()
        return
    raise SystemExit(f"unknown operation: {operation}")


if __name__ == "__main__":
    main()
