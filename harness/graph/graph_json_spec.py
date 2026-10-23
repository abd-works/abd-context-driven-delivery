"""A loaded graph keeps a serialized copy in the folder's .context."""

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from graph import Graph

_CLASS = "export class Cart {\n  total() { return 1; }\n}\n"


def _names(graph: Graph) -> list[str]:
    practice = graph.practice("clean_engineering")
    return [node.name for group in practice.nodes.values() for node in group]


def _stamp_saved(root: Path, name: str, stamp: float) -> None:
    path = root / ".context" / "graph.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    for row in document["practices"]["clean_engineering"]["nodes"]:
        if row[1] == "Cart":
            row[1] = name
    path.write_text(json.dumps(document), encoding="utf-8")
    os.utime(path, (stamp, stamp))


with description("a graph"):
    with context("that has loaded a folder"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            source = self.root / "src"
            source.mkdir()
            self.source_file = source / "cart.ts"
            self.source_file.write_text(_CLASS, encoding="utf-8")
            self.graph = Graph()
            self.graph.load_working_copy(str(self.root), {"clean_engineering": str(self.root)})

        with after.each:
            shutil.rmtree(self.root, ignore_errors=True)

        with it("should save serialized json in the folder context"):
            saved = json.loads((self.root / ".context" / "graph.json").read_text(encoding="utf-8"))
            names = [row[1] for row in saved["practices"]["clean_engineering"]["nodes"]]
            expect(names).to(contain("Cart"))

        with it("should load the saved json after the folder date moves"):
            cache = self.root / ".context" / "graph.json"
            saved = json.loads(cache.read_text(encoding="utf-8"))
            for row in saved["practices"]["clean_engineering"]["nodes"]:
                if row[1] == "Cart":
                    row[1] = "SavedCart"
            cache.write_text(json.dumps(saved), encoding="utf-8")
            os.utime(self.root, None)
            fresh = Graph()
            fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)})
            expect(_names(fresh)).to(contain("SavedCart"))

        with context("with a saved graph newer than the folder and the rules"):
            with before.each:
                _stamp_saved(self.root, "SavedCart", time.time() + 3600)

            with it("should load the saved json"):
                fresh = Graph()
                fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)})
                expect(_names(fresh)).to(contain("SavedCart"))

        with context("with a file newer than the saved graph"):
            with before.each:
                ahead = time.time() + 3600
                _stamp_saved(self.root, "SavedCart", ahead)
                os.utime(self.source_file, (ahead + 60, ahead + 60))

            with it("should reload the folder"):
                fresh = Graph()
                fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)})
                expect(_names(fresh)).to(contain("Cart"))

        with context("with a rule file newer than the saved graph"):
            with before.each:
                old = 1_000_000_000
                _stamp_saved(self.root, "SavedCart", old + 5)
                os.utime(self.source_file, (old, old))
                os.utime(self.root / "src", (old, old))
                os.utime(self.root, (old, old))

            with it("should reload"):
                fresh = Graph()
                fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)})
                expect(_names(fresh)).to(contain("Cart"))

        with context("that is forced to reload"):
            with before.each:
                _stamp_saved(self.root, "SavedCart", time.time() + 3600)

            with it("should save the rebuilt graph"):
                fresh = Graph()
                fresh.load_working_copy(
                    str(self.root),
                    {"clean_engineering": str(self.root)},
                    force=True,
                )
                saved = json.loads((self.root / ".context" / "graph.json").read_text(encoding="utf-8"))
                names = [row[1] for row in saved["practices"]["clean_engineering"]["nodes"]]
                expect(names).to(contain("Cart"))

        with context("with a saved graph that already holds extra practices"):
            with before.each:
                ahead = time.time() + 3600
                cache = self.root / ".context" / "graph.json"
                saved = json.loads(cache.read_text(encoding="utf-8"))
                for row in saved["practices"]["clean_engineering"]["nodes"]:
                    if row[1] == "Cart":
                        row[1] = "SavedCart"
                saved["practices"]["stories"] = {
                    "source_root": str(self.root),
                    "nodes": [["stories:Practice:.:stories", "stories", "Practice", "stories", ".", 1, 1, "", ""]],
                    "edges": [],
                    "rules": [],
                }
                cache.write_text(json.dumps(saved), encoding="utf-8")
                os.utime(cache, (ahead, ahead))
                os.utime(self.source_file, (ahead - 60, ahead - 60))
                os.utime(self.root / "src", (ahead - 60, ahead - 60))
                os.utime(self.root, (ahead - 60, ahead - 60))

            with it("should load a subset of the saved practices"):
                fresh = Graph()
                message = fresh.load_working_copy(
                    str(self.root),
                    {"clean_engineering": str(self.root)},
                )
                expect(message).to(equal("Loaded the saved graph."))
                expect(_names(fresh)).to(contain("SavedCart"))

            with it("should keep other practices when saving a different load"):
                other = Graph()
                other.load_working_copy(str(self.root), {"bdd": str(self.root)}, force=True)
                saved = json.loads((self.root / ".context" / "graph.json").read_text(encoding="utf-8"))
                expect(sorted(saved["practices"])).to(equal(["bdd", "clean_engineering", "stories"]))
