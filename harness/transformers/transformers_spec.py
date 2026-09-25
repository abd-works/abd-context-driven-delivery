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
from practices.bdd.model.transformation.bdd_transformer import BddTransformer
from mamba import before, description, it

from harness.transformers.logical_dump import write_temp
from harness.transformers.transformers import Transformers
from practices.clean_engineering.model.field_types import Relationship
from practices.clean_engineering.model.transformation.clean_engineering_transformer import (
    CleanEngineeringTransformer,
)
from practices.stories.model.transformation.story_map_transformer import StoryMapTransformer

_MM3E = _REPO_ROOT / "harness" / "transformers" / "fixtures" / "mm3e"
_FIXTURE_SKETCH = _MM3E / "mm3e-sketch.md"
_EXPECTED = _MM3E / "expected"
_ACTUAL = _MM3E / "actual"
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
        changed = []
        for key in sorted(set(fixture_keys) & set(emitted_keys)):
            left = fixture_members[fixture_keys[key]]
            right = emitted_members[emitted_keys[key]]
            if left["kind"] != right["kind"] or left["params"] != right["params"]:
                changed.append(
                    {
                        "member": fixture_keys[key],
                        "fixture": {"kind": left["kind"], "params": left["params"]},
                        "emitted": {"kind": right["kind"], "params": right["params"]},
                    }
                )
        if changed:
            row["member_shape"] = changed
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
    with before.all:
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
        self.fixture_ce = self.catalog.from_directory(_EXPECTED)
        self.emitted_ce = self.catalog.from_files(self.ce_files)
        self.ce_delta = self.catalog.compare(self.fixture_ce, self.emitted_ce)
        write_temp(self.roots, _ACTUAL)

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

    with it("should import Trait from the checks module that defines it"):
        source = self.ce_files["src/ability/ability.py"]
        expect("from checks.trait import Trait" in source).to(equal(True))

    with description("a generated class"):
        with description("that used constructor_parameters"):
            with before.each:
                roots = Transformers().transform_sketch("ce:\n  shop/\n    Cart\n")
                cart = roots[0].modules[0].classes[0]
                cart.relationships.append(Relationship(target="Catalog", kind="association"))
                self.source = roots[0].render("logical")["src/shop/cart.py"]

            with it("should pass use-explicit-dependencies"):
                expect(
                    "def __init__(self, catalog: Catalog) -> None:\n        self._catalog = catalog"
                    in self.source
                    and "Catalog()" not in self.source
                ).to(equal(True))

    with description("a generated description"):
        with description("that used domain_subject"):
            with before.each:
                roots = Transformers().transform_sketch(
                    "bdd:\n"
                    "a cart\n"
                    "  that has lines\n"
                    "    it should total the lines\n"
                )
                self.bdd = next(root for root in roots if isinstance(root, BddTransformer))
                self.source = self.bdd.render("logical")["tests/a_cart_spec.py"]

            with it("should pass test-observable-behavior"):
                expect(self.source).to(
                    equal(
                        "from mamba import before, description, it\n"
                        "from expects import expect\n"
                        "\n"
                        "with description(\"a cart\"):\n"
                        "    with description(\"that has lines\"):\n"
                        "        with before.each:\n"
                        "            ...\n"
                        "        with it(\"should total the lines\"):\n"
                        "            ...\n"
                    )
                )
