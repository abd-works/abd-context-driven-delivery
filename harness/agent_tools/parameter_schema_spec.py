"""Specs for the schema MCP publishes for a tool's parameters, read from its type hints."""
import sys
from pathlib import Path
from typing import TypedDict

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from harness.agent_tools.parameter_schema import ParameterSchema
from harness.mcp._examples.parameter_types.parameter_types import ParameterTypes


class _Wanted(TypedDict, total=False):
    """What a caller may ask for, every key of it optional."""

    types: list[str]
    violations: bool


class _Named(TypedDict):
    """What a caller must name."""

    name: str


def _filtered(filter: _Wanted | None = None) -> None:
    """A tool that takes an optional request."""


def _named(named: _Named) -> None:
    """A tool that takes a request with a required key."""


with description("the schema of a tool's parameters") as self:
    with context("with a request whose keys are all optional"):
        with before.each:
            self.request = ParameterSchema(_filtered).json_schema["properties"]["filter"]["anyOf"][0]

        with it("should describe each key with its type"):
            expect(self.request["properties"]).to(equal({"types": {"type": "array", "items": {"type": "string"}}, "violations": {"type": "boolean"}}))

        with it("should require none of its keys"):
            expect("required" in self.request).to(equal(False))

    with context("with a request that requires a key"):
        with it("should require that key"):
            expect(ParameterSchema(_named).json_schema["properties"]["named"]["required"]).to(equal(["name"]))

    with context("with a record declared under postponed annotations that marks a key not required"):
        with it("should require only the keys it does not mark"):
            record = ParameterSchema(ParameterTypes().echo_record).json_schema["properties"]["record"]
            expect(record["required"]).to(equal(["toolset"]))
