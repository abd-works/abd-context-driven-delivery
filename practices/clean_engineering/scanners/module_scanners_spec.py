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
from practices.bdd.spec_helpers import (  # noqa: E402
    expect_scan_fails,
    expect_scan_passes,
)
from deep_module_scanner import DeepModuleScanner  # noqa: E402
from information_hiding_scanner import InformationHidingScanner  # noqa: E402
from low_coupling_scanner import LowCouplingScanner  # noqa: E402
from module_scanner import collect_module_files  # noqa: E402
from named_seam_and_constraint_scanner import NamedSeamAndConstraintScanner  # noqa: E402
from no_subtype_at_modules_scanner import NoSubtypeAtModulesScanner  # noqa: E402
from modules_not_model_blocks_scanner import ModulesNotModelBlocksScanner  # noqa: E402
from language_modules_one_section_scanner import (  # noqa: E402
    LanguageModulesOneSectionScanner,
)
from physical_folder_scanner import PhysicalFolderScanner  # noqa: E402
from public_seam_only_scanner import PublicSeamOnlyScanner  # noqa: E402
from scan import Scan, ScannerCollection  # noqa: E402


_GOOD_CONTEXT = """
# Cart

*Cart* is the shopping-cart module.

**Seam**: `Cart.place_order`, `Cart.add_item`.
**Constraint**: callers may not mutate cart state after checkout.

## Public API

- `Cart` - running tally.
""".strip()


class Files:
    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def make_module(self, folder: "ModuleFolder") -> Path:
        path = folder.root / folder.name
        self.write(path / ".context" / "module-context.md", folder.context_body)
        for filename, content in folder.files.items():
            self.write(path / filename, content)
        return path

    def run(self, probe: "ScannerProbe"):
        scanner = probe.scanner_class(probe.rule)
        files = collect_module_files(probe.root)
        return scanner.scan(probe.root, files)


class ModuleFolder:
    def __init__(self, root: Path, name: str) -> None:
        self.root = root
        self.name = name
        self.context_body = _GOOD_CONTEXT
        self.files: dict[str, str] = {}

    def fill(self, files: dict[str, str]) -> "ModuleFolder":
        self.files = files
        return self

    def with_context(self, body: str) -> "ModuleFolder":
        self.context_body = body
        return self


class ScannerProbe:
    def __init__(self, scanner_class, root: Path) -> None:
        self.scanner_class = scanner_class
        self.root = root
        self.rule = ""

    def named(self, rule: str) -> "ScannerProbe":
        self.rule = rule
        return self


_MINIMAL_CONTEXT = "# Cart\n\nA cart.\n"


_SCANNERS_DIR = Path(__file__).resolve().parent


class _PhysicalFolderScan(Scan):
    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(
            module_dir=_SCANNERS_DIR, root_path=_SCANNERS_DIR
        )


with description("physical-folder scanner"):
    with context("a module with context file and Python content"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should produce no violations"):
            expect_scan_passes(
                _PhysicalFolderScan(),
                self.root / "cart" / "cart.py",
                rule="physical-folder",
                root=self.root,
            )

    with context("a module folder with context file but no Python files"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "empty_module"))
            Files().write(self.root / "empty_module" / "seed.py", "x = 1\n")

        with it("should flag the module when only test/junk files exist"):
            (self.root / "empty_module" / "seed.py").unlink()
            violations = Files().run(ScannerProbe(PhysicalFolderScanner, self.root).named("physical-folder"))
            expect(len(violations) >= 1).to(be_true)


    with context("a module-context.md living under .context/sessions"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            self.session_mod = (
                self.root / ".context" / "sessions" / "sprint" / "config"
            )
            Files().write(
                self.session_mod / ".context" / "module-context.md",
                _GOOD_CONTEXT,
            )
            Files().write(self.session_mod / "controller.py", "class Controller:\n    pass\n")

        with it("should flag module-context written in the session folder"):
            expect_scan_fails(
                _PhysicalFolderScan(),
                self.session_mod / "controller.py",
                rule="physical-folder",
                root=self.root,
            )


with description("named-seam-and-constraint scanner"):
    with context("a context file with seam, constraint, and public api heading"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should produce no violations"):
            violations = Files().run(ScannerProbe(NamedSeamAndConstraintScanner, self.root).named("named-seam-and-constraint"))
            expect(violations).to(equal([]))

    with context("a context file missing seam, constraint, and public api heading"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "cart").with_context(_MINIMAL_CONTEXT).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should flag seam and constraint when both are missing"):
            violations = Files().run(ScannerProbe(NamedSeamAndConstraintScanner, self.root).named("named-seam-and-constraint"))
            expect(len(violations)).to(equal(2))


with description("deep-module scanner"):
    with context("a module whose public exports exceed 40% of top-level symbols"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = "\n".join(f"class Public{i}:\n    pass\n" for i in range(8))
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": body}))

        with it("should flag the module"):
            violations = Files().run(ScannerProbe(DeepModuleScanner, self.root).named("deep-module"))
            expect(len(violations) >= 1).to(be_true)

    with context("a module with a small public seam and many internal helpers"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = "class Cart:\n    pass\n" + "\n".join(
                f"class _Helper{i}:\n    pass\n" for i in range(7)
            )
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": body}))

        with it("should produce no violations"):
            violations = Files().run(ScannerProbe(DeepModuleScanner, self.root).named("deep-module"))
            expect(violations).to(equal([]))


with description("low-coupling scanner"):
    with context("a module that imports from many siblings"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            for i in range(10):
                Files().make_module(ModuleFolder(self.root, f"sibling{i}").fill({"__init__.py": "", f"m{i}.py": "value = 1\n"}))
            imports = "\n".join(f"import sibling{i}" for i in range(10))
            Files().make_module(ModuleFolder(self.root, "hub").fill({"hub.py": f"{imports}\n\nclass Hub:\n    pass\n"}))

        with it("should flag the hub for excessive fan-out"):
            violations = Files().run(ScannerProbe(LowCouplingScanner, self.root).named("low-coupling"))
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
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": body}))

        with it("should flag the method"):
            violations = Files().run(ScannerProbe(ComplexityAbsorptionScanner, self.root).named("complexity-absorption"))
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
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": body}))

        with it("should produce no violations"):
            violations = Files().run(ScannerProbe(ComplexityAbsorptionScanner, self.root).named("complexity-absorption"))
            expect(violations).to(equal([]))


with description("use-typed-signatures scanner"):
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
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": body}))

        with it("should flag the return type"):
            violations = Files().run(ScannerProbe(InformationHidingScanner, self.root).named("use-typed-signatures"))
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
            Files().make_module(ModuleFolder(self.root, "cart").fill({"cart.py": body}))

        with it("should produce no violations"):
            violations = Files().run(ScannerProbe(InformationHidingScanner, self.root).named("use-typed-signatures"))
            expect(violations).to(equal([]))


_LEAKY_CONTEXT = """
# Cart

## Purpose

Shopping cart.

## Seam

Cart, _CartLog, CliParticipant

## Internal design

Private helpers and pickup heuristics.

## Dependencies

none
""".strip()

_PUBLIC_SEAM_CONTEXT = """
# Cart

## Purpose

Shopping cart for placing orders.

## Seam

Cart

## Public API

- `Cart.add_item` / `Cart.place_order`

## Constraint

Callers must not mutate cart state after checkout.

## Extend

Subclass only via documented variation points on Cart; do not reach into helpers.

## Dependencies

- `catalog` (one-way)
""".strip()

_MARKER_OK_CONTEXT = """
# Tools

## Purpose

Toolset annotations.

## Seam

toolset, agent_tool

## Extend

| Annotation | Marker |
|---|---|
| `@toolset` | `_is_toolset` |

## Dependencies

none
""".strip()


with description("public-seam-only scanner"):
    with context("a module-context that lists underscore types and Internal design"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "cart").with_context(_LEAKY_CONTEXT).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should flag forbidden heading and private names"):
            violations = Files().run(ScannerProbe(PublicSeamOnlyScanner, self.root).named("public-seam-only"))
            expect(len(violations) >= 2).to(be_true)
            messages = " ".join(v.message for v in violations)
            expect("Internal design" in messages or "internal design" in messages.lower()).to(
                be_true
            )
            expect("_CartLog" in messages or "_Cli" in messages or "private" in messages.lower()).to(
                be_true
            )

    with context("a module-context that is use / extend / dependencies only"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "cart").with_context(_PUBLIC_SEAM_CONTEXT).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should produce no violations"):
            violations = Files().run(ScannerProbe(PublicSeamOnlyScanner, self.root).named("public-seam-only"))
            expect(violations).to(equal([]))

    with context("a module-context that documents public _is_* authoring markers"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            Files().make_module(ModuleFolder(self.root, "tools").with_context(_MARKER_OK_CONTEXT).fill({"tools.py": "class Toolset:\n    pass\n"}))

        with it("should allow _is_* markers under Extend"):
            violations = Files().run(ScannerProbe(PublicSeamOnlyScanner, self.root).named("public-seam-only"))
            expect(violations).to(equal([]))


with description("no-subtype-at-modules scanner"):
    with context("a module-context with is-a headings"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                _GOOD_CONTEXT
                + "\n\n### AgentOperation *is a type of* AgentTool\n\n## Child : Parent\n"
            )
            Files().make_module(ModuleFolder(self.root, "cart").with_context(body).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should flag is-a and Child : Parent"):
            violations = Files().run(ScannerProbe(NoSubtypeAtModulesScanner, self.root).named("no-subtype-at-modules"))
            expect(len(violations) >= 2).to(be_true)


with description("modules-not-model-blocks scanner"):
    with context("a module-context with a typed dump and Sources"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                _GOOD_CONTEXT
                + "\n\n**Sources / context:** `cart.py`\n\n"
                + "+ Cart()\n------\nLive instance: items\n"
            )
            Files().make_module(ModuleFolder(self.root, "cart").with_context(body).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should flag model dump, Sources, and Live instance"):
            violations = Files().run(ScannerProbe(ModulesNotModelBlocksScanner, self.root).named("modules-not-model-blocks"))
            expect(len(violations) >= 3).to(be_true)


with description("language-modules-one-section scanner"):
    with context("a module-context that splits ## Language and ## Modules"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                "## Language\n\n*Cart* is the tally.\n\n"
                "## Modules\n\nBuild order: `cart`\n\n# cart\n"
            )
            Files().make_module(ModuleFolder(self.root, "cart").with_context(body).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should flag Language and Modules wrapper headings"):
            violations = Files().run(ScannerProbe(LanguageModulesOneSectionScanner, self.root).named("language-modules-one-section"))
            expect(len(violations) >= 2).to(be_true)

    with context("a module-context with language on each # path"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.root = Path(self.tmp.name)
            body = (
                "# cart\n\n*Cart* is the tally.\n\n"
                "- **Purpose:** Owns checkout.\n"
                "- **Seam (terms):** Cart\n"
            )
            Files().make_module(ModuleFolder(self.root, "cart").with_context(body).fill({"cart.py": "class Cart:\n    pass\n"}))

        with it("should produce no violations"):
            violations = Files().run(ScannerProbe(LanguageModulesOneSectionScanner, self.root).named("language-modules-one-section"))
            expect(violations).to(equal([]))

