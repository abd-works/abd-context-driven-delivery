"""Graph rules — same fault/clean pairs as historical Clean Engineering scanner specs."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import be_true, equal, expect
from mamba import context, description, it

from harness.graph.ce_multi_language_fixtures import (
    _ELIMINATE_DUPLICATION_CLEAN,
    _ELIMINATE_DUPLICATION_FAULT,
    _KEEP_OPERATIONS_SMALL_FOCUSED_CLEAN,
    _KEEP_OPERATIONS_SMALL_FOCUSED_FAULT,
    _NEVER_SWALLOW_EXCEPTIONS_CLEAN,
    _NEVER_SWALLOW_EXCEPTIONS_FAULT,
    _SIMPLIFY_CONTROL_FLOW_CLEAN,
    _SIMPLIFY_CONTROL_FLOW_FAULT,
    _USE_CLEAR_FUNCTION_PARAMETERS_CLEAN,
    _USE_CLEAR_FUNCTION_PARAMETERS_FAULT,
    _USE_EXPLICIT_DEPENDENCIES_CLEAN,
    _USE_EXPLICIT_DEPENDENCIES_FAULT,
    _USE_EXCEPTIONS_PROPERLY_CLEAN,
    _USE_EXCEPTIONS_PROPERLY_FAULT,
)
from harness.graph.ce_rule_eval_harness import assert_python_example_pair, assert_rule_pair

_LANGS = ("python", "typescript", "javascript")

_PYTHON_EXAMPLE_SLUGS = (
    "keep-operations-small-focused",
    "use-explicit-dependencies",
    "eliminate-duplication",
    "avoid-vague-parameter-names",
    "limit-operation-parameters",
    "use-property-not-accessor",
)


def _assert_multilang(slug: str, fault: dict, clean: dict) -> None:
    for lang in _LANGS:
        assert_rule_pair(slug, fault[lang], clean[lang], lang=lang)


def _example_pair(slug: str) -> None:
    assert_python_example_pair(slug)


with description("Clean Engineering graph rules (python .examples pairs)"):
    with context("keep-operations-small-focused"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("keep-operations-small-focused")
    with context("use-explicit-dependencies"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-explicit-dependencies")
    with context("eliminate-duplication"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("eliminate-duplication")
    with context("avoid-vague-parameter-names"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("avoid-vague-parameter-names")
    with context("limit-operation-parameters"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("limit-operation-parameters")
    with context("use-property-not-accessor"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-property-not-accessor")
    with context("use-consistent-naming"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-consistent-naming")
    with context("prefer-instance-operations"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("prefer-instance-operations")


with description("Clean Engineering graph rules (multi-language scanner fixtures)"):
    with context("keep-operations-small-focused"):
        with it("should flag fault snippets in python, typescript, and javascript"):
            _assert_multilang(
                "keep-operations-small-focused",
                _KEEP_OPERATIONS_SMALL_FOCUSED_FAULT,
                _KEEP_OPERATIONS_SMALL_FOCUSED_CLEAN,
            )

    with context("simplify-control-flow"):
        with it("should flag fault snippets in python, typescript, and javascript"):
            _assert_multilang(
                "simplify-control-flow",
                _SIMPLIFY_CONTROL_FLOW_FAULT,
                _SIMPLIFY_CONTROL_FLOW_CLEAN,
            )

    with context("eliminate-duplication"):
        with it("should flag fault snippets in python, typescript, and javascript"):
            _assert_multilang(
                "eliminate-duplication",
                _ELIMINATE_DUPLICATION_FAULT,
                _ELIMINATE_DUPLICATION_CLEAN,
            )

    with context("limit-operation-parameters"):
        with it("should flag too many parameters (historical use-clear-function-parameters fault)"):
            _assert_multilang(
                "limit-operation-parameters",
                _USE_CLEAR_FUNCTION_PARAMETERS_FAULT,
                _USE_CLEAR_FUNCTION_PARAMETERS_CLEAN,
            )

    with context("use-explicit-dependencies"):
        with it("should flag constructor `new` in python, typescript, and javascript"):
            _assert_multilang(
                "use-explicit-dependencies",
                _USE_EXPLICIT_DEPENDENCIES_FAULT,
                _USE_EXPLICIT_DEPENDENCIES_CLEAN,
            )

    with context("use-exceptions-properly"):
        with it("should flag bare catch in python, typescript, and javascript"):
            _assert_multilang(
                "use-exceptions-properly",
                _USE_EXCEPTIONS_PROPERLY_FAULT,
                _USE_EXCEPTIONS_PROPERLY_CLEAN,
            )

    with context("never-swallow-exceptions"):
        with it("should flag empty catch in python, typescript, and javascript"):
            _assert_multilang(
                "never-swallow-exceptions",
                _NEVER_SWALLOW_EXCEPTIONS_FAULT,
                _NEVER_SWALLOW_EXCEPTIONS_CLEAN,
            )
