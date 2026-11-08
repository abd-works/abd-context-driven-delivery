"""A loaded graph keeps a serialized copy in the folder's .context."""

import json
import os
import shutil
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent

from expects import contain, equal, expect
from harness.installation.destination import data_of  # noqa: E402
from mamba import after, before, context, description, it

from harness.graph.graph import Graph

_CLASS = "export class Cart {\n  total() { return 1; }\n}\n"


def _names(graph: Graph) -> list[str]:
    practice = graph.practice("clean_engineering")
    return [node.name for node in practice.graph.nodes_of(practice)]


def _stamp_saved(root: Path, name: str, stamp: float) -> None:
    path = root / ".context" / "graph.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    for node in document["practices"]["clean_engineering"]["nodes"]:
        if node["name"] == "Cart":
            node["name"] = name
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
            data_of(self.graph.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}))

        with after.each:
            shutil.rmtree(self.root, ignore_errors=True)

        with it("should save serialized json in the folder context"):
            saved = json.loads((self.root / ".context" / "graph.json").read_text(encoding="utf-8"))
            names = [node["name"] for node in saved["practices"]["clean_engineering"]["nodes"]]
            expect(names).to(contain("Cart"))

        with it("should load the saved json after the folder date moves"):
            cache = self.root / ".context" / "graph.json"
            saved = json.loads(cache.read_text(encoding="utf-8"))
            for node in saved["practices"]["clean_engineering"]["nodes"]:
                if node["name"] == "Cart":
                    node["name"] = "SavedCart"
            cache.write_text(json.dumps(saved), encoding="utf-8")
            os.utime(self.root, None)
            fresh = Graph()
            data_of(fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}))
            expect(_names(fresh)).to(contain("SavedCart"))

        with context("with a saved graph newer than the folder and the rules"):
            with before.each:
                _stamp_saved(self.root, "SavedCart", time.time() + 3600)

            with it("should load the saved json"):
                fresh = Graph()
                data_of(fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}))
                expect(_names(fresh)).to(contain("SavedCart"))

        with context("with a file changed after the saved graph was written"):
            with before.each:
                ahead = time.time() + 3600
                _stamp_saved(self.root, "SavedCart", ahead)
                os.utime(self.source_file, (ahead + 60, ahead + 60))

            with it("should load the saved json, since nothing watches the files"):
                fresh = Graph()
                data_of(fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}))
                expect(_names(fresh)).to(contain("SavedCart"))

            with it("should read the changed file once it is refreshed"):
                fresh = Graph()
                data_of(fresh.load_working_copy(str(self.root), {"clean_engineering": str(self.root)}))
                data_of(fresh.refresh([str(self.source_file)]))
                expect(_names(fresh)).to(contain("Cart"))

        with context("that is forced to reload"):
            with before.each:
                _stamp_saved(self.root, "SavedCart", time.time() + 3600)

            with it("should save the rebuilt graph"):
                fresh = Graph()
                data_of(fresh.load_working_copy(
                    str(self.root),
                    {"clean_engineering": str(self.root)},
                    force=True,
                ))
                saved = json.loads((self.root / ".context" / "graph.json").read_text(encoding="utf-8"))
                names = [node["name"] for node in saved["practices"]["clean_engineering"]["nodes"]]
                expect(names).to(contain("Cart"))

        with context("with a saved graph that already holds extra practices"):
            with before.each:
                ahead = time.time() + 3600
                cache = self.root / ".context" / "graph.json"
                saved = json.loads(cache.read_text(encoding="utf-8"))
                for node in saved["practices"]["clean_engineering"]["nodes"]:
                    if node["name"] == "Cart":
                        node["name"] = "SavedCart"
                saved["practices"]["stories"] = {
                    "source_root": str(self.root),
                    "nodes": [{"node_id": "stories:Practice:.:stories", "name": "stories", "type": "Practice", "practice": "stories"}],
                    "edges": [],
                    "violations": [],
                }
                cache.write_text(json.dumps(saved), encoding="utf-8")
                os.utime(cache, (ahead, ahead))
                os.utime(self.source_file, (ahead - 60, ahead - 60))
                os.utime(self.root / "src", (ahead - 60, ahead - 60))
                os.utime(self.root, (ahead - 60, ahead - 60))

            with it("should load a subset of the saved practices"):
                fresh = Graph()
                message = data_of(fresh.load_working_copy(
                    str(self.root),
                    {"clean_engineering": str(self.root)},
                ))
                expect(message["message"]).to(equal("Loaded the saved graph."))
                expect(_names(fresh)).to(contain("SavedCart"))

            with it("should keep other practices when saving a different load"):
                other = Graph()
                data_of(other.load_working_copy(str(self.root), {"bdd": str(self.root)}, force=True))
                saved = json.loads((self.root / ".context" / "graph.json").read_text(encoding="utf-8"))
                expect(sorted(saved["practices"])).to(equal(["bdd", "clean_engineering", "stories"]))
