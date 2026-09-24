"""BDD spec — compare Transformers logical python to the mm3e fixture."""

import ast
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import before, description, it

from harness.transformers.transformers import Transformers
from practices.clean_engineering.model.transformation.clean_engineering_transformer import (
    CleanEngineeringTransformer,
)
from practices.stories.model.transformation.story_map_transformer import StoryMapTransformer

_FIXTURE_SKETCH = _REPO_ROOT / "harness" / "transformers" / "fixtures" / "mm3e" / "mm3e-sketch.md"
_FIXTURE_PYTHON = _REPO_ROOT / "harness" / "transformers" / "fixtures" / "mm3e"
_SNAKE = re.compile(r"([a-z0-9])([A-Z])")


class Mm3ePythonCatalog:
    """Classes, bases, and members from a path→source map (fixture or transformer emit)."""

    def from_directory(self, root: Path) -> dict[str, dict]:
        files = {}
        for path in sorted(root.rglob("*.py")):
            files[str(path.relative_to(root)).replace("\\", "/")] = path.read_text(
                encoding="utf-8"
            )
        return self.from_files(files)

    def from_files(self, files: dict[str, str]) -> dict[str, dict]:
        catalog: dict[str, dict] = {}
        for text in files.values():
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    catalog[node.name] = self._class_entry(node)
        return catalog

    def compare(self, fixture: dict[str, dict], emitted: dict[str, dict]) -> dict:
        missing_classes = sorted(set(fixture) - set(emitted))
        extra_classes = sorted(set(emitted) - set(fixture))
        classes: dict[str, dict] = {}
        for name in sorted(set(fixture) & set(emitted)):
            row = self._class_delta(fixture[name], emitted[name])
            if row:
                classes[name] = row
        delta = {}
        if missing_classes:
            delta["missing_classes"] = missing_classes
        if extra_classes:
            delta["extra_classes"] = extra_classes
        if classes:
            delta["classes"] = classes
        return delta

    def _class_delta(self, fixture: dict, emitted: dict) -> dict:
        row: dict = {}
        fixture_bases = [b for b in fixture["bases"] if b not in {"ABC", "object", ""}]
        emitted_bases = [b for b in emitted["bases"] if b not in {"ABC", "object", ""}]
        if fixture_bases != emitted_bases:
            row["bases"] = {"fixture": fixture_bases, "emitted": emitted_bases}
        fixture_members = fixture["members"]
        emitted_members = emitted["members"]
        fixture_keys = {self._snake(name): name for name in fixture_members}
        emitted_keys = {self._snake(name): name for name in emitted_members}
        missing = sorted(set(fixture_keys) - set(emitted_keys))
        extra = sorted(set(emitted_keys) - set(fixture_keys))
        renamed = sorted(
            (fixture_keys[key], emitted_keys[key])
            for key in sorted(set(fixture_keys) & set(emitted_keys))
            if fixture_keys[key] != emitted_keys[key]
        )
        if missing:
            row["missing_members"] = [fixture_keys[key] for key in missing]
        if extra:
            row["extra_members"] = [emitted_keys[key] for key in extra]
        if renamed:
            row["member_names"] = [
                {"fixture": left, "emitted": right} for left, right in renamed
            ]
        return row

    def _class_entry(self, node: ast.ClassDef) -> dict:
        members: dict[str, dict] = {}
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name in {"__init__",}:
                    continue
                kind = "property" if self._is_property(item) else "method"
                members[item.name] = {
                    "kind": kind,
                    "params": [arg.arg for arg in item.args.args if arg.arg != "self"],
                }
                continue
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                members[item.target.id] = {"kind": "property", "params": []}
        return {
            "bases": [self._expr_name(base) for base in node.bases],
            "members": members,
        }

    def _is_property(self, node: ast.FunctionDef) -> bool:
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return True
        return False

    def _expr_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ast.dump(node)

    def _snake(self, name: str) -> str:
        return _SNAKE.sub(r"\1_\2", name).strip().lower()


with description("Transformers"):
    with before.each:
        self.sketch = _FIXTURE_SKETCH.read_text(encoding="utf-8")
        self.roots = Transformers().transform_sketch(self.sketch)
        self.story_map = next(
            root for root in self.roots if isinstance(root, StoryMapTransformer)
        )
        self.ce = next(
            root for root in self.roots if isinstance(root, CleanEngineeringTransformer)
        )
        self.files = self.story_map.render("logical")
        self.ce_files = self.ce.render("logical")
        self.catalog = Mm3ePythonCatalog()
        self.fixture_ce = self.catalog.from_directory(_FIXTURE_PYTHON)
        self.emitted_ce = self.catalog.from_files(self.ce_files)
        self.ce_delta = self.catalog.compare(self.fixture_ce, self.emitted_ce)

    with it("should load StoryMapTransformer from the stories lens"):
        expect(self.story_map.epics[0].name).to(equal("Resolve Checks"))
        expect(self.story_map.epics[0].sub_epics[0].name).to(equal("Make Check"))
        expect(self.story_map.epics[0].sub_epics[0].stories[0].name).to(
            equal("Make Trait Check")
        )

    with it("should write the python story file under the epic and sub-epic folders"):
        path = (
            "tests/resolve-checks/make-check/make-trait-check/"
            "make_trait_check_story.test.py"
        )
        expect(path in self.files).to(equal(True))

    with it("should emit every class and member from the mm3e python fixture"):
        expect(self.ce_delta.get("missing_classes", [])).to(equal([]))
        expect(self.ce_delta.get("extra_classes", [])).to(equal([]))
        expect(self.ce_delta.get("classes", {})).to(equal({}))
