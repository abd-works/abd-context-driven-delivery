"""BDD development — create a database in a different repo.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a knowledge graph … that has been pointed at a different repo
"""
from pathlib import Path
import sys
import tempfile

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import after, before, context, description, it

from practices.clean_engineering.clean_engineering import CleanEngineering  # noqa: F401
from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph


with description("KnowledgeGraph.create_database"):
    with it("should be marked for mcp skill and agent tool"):
        fn = KnowledgeGraph.create_database
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(True))


with description("a knowledge graph"):
    with context("that has been pointed at a different repo"):
        with before.all:
            self.folder = tempfile.TemporaryDirectory()
            self.repo = Path(self.folder.name)
            (self.repo / "hello.py").write_text(
                "class Hello:\n    pass\n",
                encoding="utf-8",
            )
            self.graph = KnowledgeGraph()
            self.graph.create_database(self.repo)

        with after.all:
            self.folder.cleanup()

        with it("should set the path to that repo"):
            expect(self.graph.root).to(equal(Path(self.repo)))

        with it("should create the database in that repo"):
            expect((self.repo / ".codeql" / "python-master" / "db-python").is_dir()).to(
                equal(True)
            )

        with it("should copy the master to the working copy"):
            expect(
                (self.repo / ".codeql" / "python-working-copy" / "db-python").is_dir()
            ).to(equal(True))

        with it("should not use the default python-db"):
            expect((self.repo / ".codeql" / "python-db").exists()).to(equal(False))
