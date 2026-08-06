"""BDD spec for context_tools/bdd/scanners — ported abd-skills BDD rules."""
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd

import sys
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scanners import ScannerCollection  # noqa: E402

_BDD_DIR = _REPO_ROOT / "context_tools" / "bdd"
_RULE = "missing-spec"
_PORTED_RULES = [
    "business-readable-language",
    "layer-isolation",
    "missing-spec",
    "no-remaining-signatures",
    "observable-behavior",
    "plain-english-only",
    "signature-markers",
]

_PRODUCTION_SOURCE = "class Widget:\n    def greet(self, name):\n        return name\n"
_FILLED_SPEC = (
    "from mamba import description, it\n\n"
    "with description('a widget'):\n"
    "    with it('should greet by name'):\n"
    "        pass\n"
)
_SIGNATURE_ONLY_SPEC = "with description('a widget'):\n    pass\n"
_HELPER_SOURCE = (
    "from greet_story import Widget\n\n"
    "class AgentHelper:\n"
    "    def given_a_widget(self):\n"
    "        return Widget()\n"
)
_UNRELATED_SPEC = (
    "from mamba import description, it\n\n"
    "with description('a shipping label'):\n"
    "    with it('should carry a destination'):\n"
    "        pass\n"
)
_PACKAGE_SPEC = (
    "from mamba import description, it\n\n"
    "from widget import Widget\n\n"
    "with description('a widget'):\n"
    "    with it('should greet by name'):\n"
    "        Widget()\n"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _scan(root: Path, rule: str = _RULE, pattern: str = "*.py") -> list:
    scanner_class = ScannerCollection(_BDD_DIR).get(rule)
    scanner = scanner_class(rule)
    if pattern == "*":
        files = sorted(p for p in root.rglob("*") if p.is_file())
    else:
        files = sorted(root.rglob(pattern))
    return scanner.scan(root, files)


with description("the BDD scan rules"):
    with it("should offer every ported abd-skills rule plus missing-spec"):
        # Arrange / Act
        rules = sorted(ScannerCollection(_BDD_DIR).discover())
        # Assert
        expect(rules).to(equal(_PORTED_RULES))


with description("a Python module that BDD governs"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write(self.root / "widget" / "widget.py", _PRODUCTION_SOURCE)

    with context("that has a sibling spec covering it"):
        with before.each:
            _write(self.root / "widget" / "widget_spec.py", _FILLED_SPEC)

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))

    with context("that has no spec file at all"):
        with it("should flag the module as unspecified"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(len(violations)).to(equal(1))

        with it("should name the missing-spec rule on the violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations[0].rule).to(equal(_RULE))

    with context("that has a spec file holding no observations"):
        with before.each:
            _write(self.root / "widget" / "widget_spec.py", _SIGNATURE_ONLY_SPEC)

        with it("should flag the spec as empty"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(len(violations)).to(equal(1))

    with context("that is covered by an agent-tier spec"):
        with before.each:
            _write(self.root / "widget" / "widget_agent_spec.py", _FILLED_SPEC)

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))

    with context("that is covered by a package spec naming its class"):
        with before.each:
            _write(self.root / "widget" / "package_spec.py", _PACKAGE_SPEC)

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))

    with context("that sits beside a package spec that never mentions it"):
        with before.each:
            _write(self.root / "widget" / "package_spec.py", _UNRELATED_SPEC)

        with it("should flag the module as unspecified"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(len(violations)).to(equal(1))


with description("a story module whose coverage lives in a test helper"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write(self.root / "greet" / "greet_story.py", _PRODUCTION_SOURCE)

    with context("that has a tier helper beside it"):
        with before.each:
            _write(self.root / "greet" / "greet_test_helper.agent.py", _HELPER_SOURCE)

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))

    with context("that has no tier helper at all"):
        with it("should flag the story as unspecified"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(len(violations)).to(equal(1))


with description("a Python file that carries no public surface"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that only re-exports through __init__.py"):
        with before.each:
            _write(self.root / "widget" / "__init__.py", "from widget import Widget\n")

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))

    with context("that defines only private helpers"):
        with before.each:
            _write(self.root / "widget" / "_helpers.py", "def _shout(text):\n    return text\n")

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))

    with context("that is itself a scanner beside a collective spec"):
        with before.each:
            _write(self.root / "scanners" / "widget_scanner.py", _PRODUCTION_SOURCE)

        with it("should report no violation"):
            # Act
            violations = _scan(self.root)
            # Assert
            expect(violations).to(equal([]))


with description("a module folder whose only Python file is unspecified"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write(self.root / "widget" / "widget.py", _PRODUCTION_SOURCE)

    with it("should point the violation at the unspecified module file"):
        # Act
        violations = _scan(self.root)
        # Assert
        expect(violations[0].location.endswith("widget.py")).to(be_true)


with description("a behavior sketch under plain-english-only"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that keeps subjects in English and call surface on arrow lines"):
        with before.each:
            _write(
                self.root / "widget-sketch.md",
                "Fidelity: behavior\n\n"
                "a widget\n"
                "  -> widget = new Widget()\n"
                "  that is greeted\n"
                "    it should greet the caller by name\n",
            )

        with it("should report no violation"):
            violations = _scan(self.root, "plain-english-only", "*")
            expect(violations).to(equal([]))

    with context("that puts a method signature in a subject line"):
        with before.each:
            _write(
                self.root / "widget-hierarchy.txt",
                "Widget\n"
                "  applyVoucher(voucherId: string)\n"
                "    should apply the discount\n",
            )

        with it("should flag the code syntax in the subject"):
            violations = _scan(self.root, "plain-english-only", "*")
            expect(len(violations) >= 1).to(be_true)
            expect(violations[0].rule).to(equal("plain-english-only"))


with description("a leaf behavior under business-readable-language"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that starts every leaf with should"):
        with before.each:
            _write(
                self.root / "widget_spec.py",
                "from mamba import description, it\n\n"
                "with description('a widget'):\n"
                "    with it('should greet by name'):\n"
                "        pass\n",
            )

        with it("should report no violation"):
            violations = _scan(self.root, "business-readable-language", "*")
            expect(violations).to(equal([]))

    with context("that uses a technical leaf label"):
        with before.each:
            _write(
                self.root / "widget_spec.py",
                "from mamba import description, it\n\n"
                "with description('a widget'):\n"
                "    with it('calls DiscountCalculator.apply'):\n"
                "        pass\n",
            )

        with it("should flag the non-should observation"):
            violations = _scan(self.root, "business-readable-language", "*")
            expect(len(violations)).to(equal(1))


with description("a signature file under signature-markers"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that keeps every it body as the marker alone"):
        with before.each:
            _write(
                self.root / "widget_spec.py",
                "from mamba import description, it\n\n"
                "with description('a widget'):\n"
                "    with it('should greet by name'):\n"
                "        # BDD: SIGNATURE\n",
            )

        with it("should report no violation"):
            violations = _scan(self.root, "signature-markers", "*")
            expect(violations).to(equal([]))

    with context("that sneaks an assertion beside the marker"):
        with before.each:
            _write(
                self.root / "widget_spec.py",
                "from mamba import description, it\n"
                "from expects import expect, equal\n\n"
                "with description('a widget'):\n"
                "    with it('should greet by name'):\n"
                "        # BDD: SIGNATURE\n"
                "        expect(1).to(equal(1))\n",
            )

        with it("should flag the leaked implementation"):
            violations = _scan(self.root, "signature-markers", "*")
            expect(len(violations)).to(equal(1))


with description("a mixed development file under no-remaining-signatures"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write(
            self.root / "widget_spec.py",
            "from mamba import description, it\n"
            "from expects import expect, equal\n\n"
            "with description('a widget'):\n"
            "    with it('should greet by name'):\n"
            "        expect('Ada').to(equal('Ada'))\n"
            "    with it('should farewell everyone greeted'):\n"
            "        # BDD: SIGNATURE\n",
        )

    with it("should flag the leftover marker"):
        violations = _scan(self.root, "no-remaining-signatures", "*")
        expect(len(violations)).to(equal(1))


with description("a development file under observable-behavior"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that asserts through the public API"):
        with before.each:
            _write(
                self.root / "widget_spec.py",
                "from mamba import description, it\n"
                "from expects import expect, equal\n\n"
                "with description('a widget'):\n"
                "    with it('should greet by name'):\n"
                "        expect(widget.label).to(equal('Ada'))\n",
            )

        with it("should report no violation"):
            violations = _scan(self.root, "observable-behavior", "*")
            expect(violations).to(equal([]))

    with context("that probes a private field"):
        with before.each:
            _write(
                self.root / "widget_spec.py",
                "from mamba import description, it\n"
                "from expects import expect, equal\n\n"
                "with description('a widget'):\n"
                "    with it('should greet by name'):\n"
                "        expect(widget._names).to(equal(['Ada']))\n",
            )

        with it("should flag the private access"):
            violations = _scan(self.root, "observable-behavior", "*")
            expect(len(violations)).to(equal(1))


with description("a development file under layer-isolation"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    with context("that mocks an external repository boundary"):
        with before.each:
            _write(
                self.root / "widget.spec.ts",
                "import { VoucherService } from '../voucher-service';\n\n"
                "jest.mock('../voucher-repository');\n\n"
                "describe('a voucher service', () => {\n"
                "  it('should persist the voucher when valid', () => {\n"
                "    expect(true).toBe(true);\n"
                "  });\n"
                "});\n",
            )

        with it("should report no violation for a non-relative internal helper name"):
            # Arrange — repository mock path is not ./relative and not an internal verb
            violations = _scan(self.root, "layer-isolation", "*")
            # Assert
            expect(violations).to(equal([]))

    with context("that mocks a relative internal module"):
        with before.each:
            _write(
                self.root / "widget.spec.ts",
                "jest.mock('./calculateDiscount');\n\n"
                "describe('a voucher', () => {\n"
                "  it('should apply the discount', () => {\n"
                "    expect(true).toBe(true);\n"
                "  });\n"
                "});\n",
            )

        with it("should flag the internal mock"):
            violations = _scan(self.root, "layer-isolation", "*")
            expect(len(violations) >= 1).to(be_true)
            expect(violations[0].rule).to(equal("layer-isolation"))
