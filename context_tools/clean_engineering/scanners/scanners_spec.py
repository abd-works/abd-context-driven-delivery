"""BDD spec for scanners/scanner-behavior.md - one repair fixture pair test per Clean Code python scanner."""

import tempfile
from pathlib import Path

from expects import be_true, equal, expect
from mamba import context, description, it

from scan import ScannerCollection

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CE_DIR = _REPO_ROOT / "context_tools" / "clean_engineering"
_EVALS_ROOT = _CE_DIR / "examples" / "evals"
_DISCOVERED = ScannerCollection(_CE_DIR).discover()


def _fixture_source(rule: str, name: str, ext: str = ".py") -> str:
    path = _EVALS_ROOT / rule / f"{name}{ext}"
    return path.read_text(encoding="utf-8")


def _scan_source(scanner_class, rule, source, suffix: str = ".py"):
    temp_dir = tempfile.TemporaryDirectory()
    root = Path(temp_dir.name)
    file_path = root / f"example{suffix}"
    file_path.write_text(source.strip() + "\n", encoding="utf-8")
    scanner = scanner_class(rule)
    return scanner.scan(root, [file_path])


def _assert_scanner_examples(rule, ext: str = ".py"):
    scanner_class = _DISCOVERED[rule]
    pass_source = _fixture_source(rule, "repairedAsset", ext)
    fail_source = _fixture_source(rule, "faultyAsset", ext)
    expect(bool(pass_source.strip())).to(be_true)
    expect(bool(fail_source.strip())).to(be_true)
    pass_violations = _scan_source(scanner_class, rule, pass_source, ext)
    fail_violations = _scan_source(scanner_class, rule, fail_source, ext)
    expect(len(pass_violations)).to(equal(0))
    expect(len(fail_violations) >= 1).to(be_true)
    for violation in fail_violations:
        expect(violation.rule).to(equal(rule))


with description("Clean Code python scanners"):
    with context("keep-operations-small-focused"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("keep-operations-small-focused")

    with context("use-intention-revealing-names"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("use-intention-revealing-names")

    with context("maintain-abstraction-levels"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("maintain-abstraction-levels")

    with context("keep-functions-single-responsibility"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("keep-functions-single-responsibility")

    with context("keep-classes-single-responsibility"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("keep-classes-single-responsibility")

    with context("eliminate-duplication"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("eliminate-duplication")

    with context("never-swallow-exceptions"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("never-swallow-exceptions")

    with context("use-clear-function-parameters"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("use-clear-function-parameters")

    with context("simplify-control-flow"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("simplify-control-flow")

    with context("use-explicit-dependencies"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("use-explicit-dependencies")

    with context("use-exceptions-properly"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("use-exceptions-properly")

    with context("separate-concerns"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("separate-concerns")

    with context("use-consistent-naming"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("use-consistent-naming")

    with context("use-domain-language"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("use-domain-language")

    with context("provide-meaningful-context"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("provide-meaningful-context")

    with context("enforce-encapsulation"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("enforce-encapsulation")

    with context("stop-writing-useless-comments"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("stop-writing-useless-comments")

    with context("reuse-existing-not-invent-parallel"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("reuse-existing-not-invent-parallel")

    with context("reuse-established-notation-not-a-parallel-one"):
        with it("should keep faultyAsset.md violating and repairedAsset.md clean"):
            _assert_scanner_examples(
                "reuse-established-notation-not-a-parallel-one", ext=".md"
            )

    with context("do-not-invent-parallel-object-models"):
        with it("should keep faultyAsset violating and repairedAsset clean"):
            _assert_scanner_examples("do-not-invent-parallel-object-models")
