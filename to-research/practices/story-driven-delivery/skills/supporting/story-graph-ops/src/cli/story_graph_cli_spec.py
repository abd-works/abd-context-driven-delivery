"""Mamba spec for CLI conversion policy and source-of-truth guard."""

import os
import sys
from argparse import Namespace
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mamba import before, context, description, it
from expects import be_true, equal, expect, raise_error

from src.cli.story_graph_cli import (
    CliError,
    _assert_conversion_policy,
    cmd_convert,
)


with description("story graph CLI conversion policy"):
    with context("when converting from model protocols to code protocols"):
        with it("should reject conversion because code is source-of-truth"):
            expect(lambda: _assert_conversion_policy("markdown", "typescript")).to(
                raise_error(CliError)
            )
            expect(lambda: _assert_conversion_policy("json", "java")).to(
                raise_error(CliError)
            )
            expect(lambda: _assert_conversion_policy("drawio", "python")).to(
                raise_error(CliError)
            )

    with context("when converting between code protocols"):
        with it("should allow conversion"):
            _assert_conversion_policy("typescript", "python")
            _assert_conversion_policy("python", "java")
            _assert_conversion_policy("java", "typescript")
            expect(True).to(be_true)

    with context("when convert command is invoked for model to code"):
        with before.each:
            self.args = Namespace(
                from_protocol="markdown",
                to_protocol="typescript",
                input=str(Path("missing.md")),
                output=str(Path("out.tree.json")),
            )

        with it("should fail fast on policy before file IO"):
            expect(lambda: cmd_convert(self.args)).to(raise_error(CliError))

    with context("when converting from model to non-code protocols"):
        with it("should stay allowed"):
            _assert_conversion_policy("markdown", "drawio")
            _assert_conversion_policy("json", "miro")
            _assert_conversion_policy("drawio", "json")
            expect(1).to(equal(1))

