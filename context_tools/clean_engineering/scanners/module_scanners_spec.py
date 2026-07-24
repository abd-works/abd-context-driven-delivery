"""BDD spec for module-level CleanEngineering scanners.

Synthesises minimal module folders in a temporary directory, then asserts each
scanner produces (or does not produce) violations against the shape.
"""

import sys
import tempfile
from pathlib import Path

from expects import be_true, equal, expect
from mamba import before, context, description, it

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from complexity_absorption_scanner import ComplexityAbsorptionScanner  # noqa: E402
from deep_module_scanner import DeepModuleScanner  # noqa: E402
from information_hiding_scanner import InformationHidingScanner  # noqa: E402
from low_coupling_scanner import LowCouplingScanner  # noqa: E402
from module_scanner import collect_module_files  # noqa: E402
from named_seam_and_constraint_scanner import NamedSeamAndConstraintScanner  # noqa: E402
from physical_folder_scanner import PhysicalFolderScanner  # noqa: E402


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_module(root: Path, name: str, context_body: str, files: dict[str, str]) -> Path:
    folder = root / name
    _write(folder / ".context" / "module-context.md", context_body)
    for filename, content in files.items():
        _write(folder / filename, content)
    return folder


_GOOD_CONTEXT = """
# Cart

*Cart* is the shopping-cart module.

**Seam**: `Cart.place_order`, `Cart.add_item`.
**Constraint**: callers may not mutate cart state after checkout.

## Public API

- `Cart` — running tally.
""".strip()

_MINIMAL_CONTEXT = "# Cart\n\nA cart.\n"


def _run(scanner_class, rule: str, root: Path):
    scanner = scanner_class(rule)
    files = collect_module_files(root)
    return scanner.scan(root, files)


with description("physical-folder scanner"):
    with context("a module with context file and Python content"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": "class Cart:\n    pass\n"})

        with it("should produce no violations"):
            violations = _run(PhysicalFolderScanner, "physical-folder", self.root)
            expect(violations).to(equal([]))

    with context("a module folder with context file but no Python files"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            _make_module(self.root, "empty_module", _GOOD_CONTEXT, {})
            _write(self.root / "empty_module" / "seed.py", "x = 1\n")

        with it("should flag the module when only test/junk files exist"):
            (self.root / "empty_module" / "seed.py").unlink()
            violations = _run(PhysicalFolderScanner, "physical-folder", self.root)
            expect(len(violations) >= 1).to(be_true)


with description("named-seam-and-constraint scanner"):
    with context("a context file with seam, constraint, and public api heading"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": "class Cart:\n    pass\n"})

        with it("should produce no violations"):
            violations = _run(
                NamedSeamAndConstraintScanner, "named-seam-and-constraint", self.root
            )
            expect(violations).to(equal([]))

    with context("a context file missing seam, constraint, and public api heading"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            _make_module(
                self.root,
                "cart",
                _MINIMAL_CONTEXT,
                {"cart.py": "class Cart:\n    pass\n"},
            )

        with it("should flag all three missing elements"):
            violations = _run(
                NamedSeamAndConstraintScanner, "named-seam-and-constraint", self.root
            )
            expect(len(violations)).to(equal(3))


with description("deep-module scanner"):
    with context("a module whose public exports exceed 40% of top-level symbols"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = "\n".join(f"class Public{i}:\n    pass\n" for i in range(8))
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": body})

        with it("should flag the module"):
            violations = _run(DeepModuleScanner, "deep-module", self.root)
            expect(len(violations) >= 1).to(be_true)

    with context("a module with a small public seam and many internal helpers"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = "class Cart:\n    pass\n" + "\n".join(
                f"class _Helper{i}:\n    pass\n" for i in range(7)
            )
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": body})

        with it("should produce no violations"):
            violations = _run(DeepModuleScanner, "deep-module", self.root)
            expect(violations).to(equal([]))


with description("low-coupling scanner"):
    with context("a module that imports from many siblings"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            for i in range(10):
                _make_module(
                    self.root,
                    f"sibling{i}",
                    _GOOD_CONTEXT,
                    {"__init__.py": "", f"m{i}.py": "value = 1\n"},
                )
            imports = "\n".join(f"import sibling{i}" for i in range(10))
            _make_module(
                self.root,
                "hub",
                _GOOD_CONTEXT,
                {"hub.py": f"{imports}\n\nclass Hub:\n    pass\n"},
            )

        with it("should flag the hub for excessive fan-out"):
            violations = _run(LowCouplingScanner, "low-coupling", self.root)
            expect(any(v.rule == "low-coupling" for v in violations)).to(be_true)


with description("complexity-absorption scanner"):
    with context("a public method with five required parameters"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                "class Cart:\n"
                "    def checkout(self, a, b, c, d, e):\n"
                "        pass\n"
            )
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": body})

        with it("should flag the method"):
            violations = _run(
                ComplexityAbsorptionScanner, "complexity-absorption", self.root
            )
            expect(len(violations) >= 1).to(be_true)

    with context("a public method with four required parameters"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                "class Cart:\n"
                "    def checkout(self, a, b, c, d):\n"
                "        pass\n"
            )
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": body})

        with it("should produce no violations"):
            violations = _run(
                ComplexityAbsorptionScanner, "complexity-absorption", self.root
            )
            expect(violations).to(equal([]))


with description("information-hiding scanner"):
    with context("a public method that returns dict[str, Any]"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                "from typing import Any\n"
                "class Cart:\n"
                "    def snapshot(self) -> dict[str, Any]:\n"
                "        return {}\n"
            )
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": body})

        with it("should flag the return type"):
            violations = _run(
                InformationHidingScanner, "information-hiding", self.root
            )
            expect(len(violations) >= 1).to(be_true)

    with context("a public method returning a domain type"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                "class Snapshot:\n"
                "    pass\n"
                "class Cart:\n"
                "    def snapshot(self) -> Snapshot:\n"
                "        return Snapshot()\n"
            )
            _make_module(self.root, "cart", _GOOD_CONTEXT, {"cart.py": body})

        with it("should produce no violations"):
            violations = _run(
                InformationHidingScanner, "information-hiding", self.root
            )
            expect(violations).to(equal([]))
