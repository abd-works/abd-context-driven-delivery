# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""BDD spec for MCP host JSON Schema binding of Python parameter types."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _path = str(_REPO_ROOT / _cat)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from expects import contain, equal, expect
from mamba import before, context, description, it

from context_tools.actions.iterate.iterate import Iterate
from mcp_server.mcp_host import _input_schema_for_callable
from mcp_server.examples.parameter_types.parameter_types import ParameterTypes


def _sorted_any_of_types(schema: dict) -> list[str]:
    return sorted(variant["type"] for variant in schema["anyOf"])


with description("an MCP host input schema"):

    with context("that has been derived from a ParameterTypes echo operation"):
        with before.each:
            self.schema = _input_schema_for_callable(ParameterTypes().echo)
            self.properties = self.schema["properties"]

        with context("with a string parameter"):
            with it("should advertise JSON Schema string"):
                expect(self.properties["text"]).to(equal({"type": "string"}))

        with context("with an integer parameter"):
            with it("should advertise JSON Schema integer"):
                expect(self.properties["count"]).to(equal({"type": "integer"}))

        with context("with a float parameter"):
            with it("should advertise JSON Schema number"):
                expect(self.properties["ratio"]).to(equal({"type": "number"}))

        with context("with a boolean parameter"):
            with it("should advertise JSON Schema boolean"):
                expect(self.properties["flag"]).to(equal({"type": "boolean"}))

        with context("with a list of strings parameter"):
            with it("should advertise JSON Schema array of string"):
                expect(self.properties["items"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

        with context("with a dict of string values parameter"):
            with it("should advertise JSON Schema object with string additionalProperties"):
                expect(self.properties["fields"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        }
                    )
                )

        with context("with an untyped list parameter"):
            with it("should advertise JSON Schema array of string"):
                expect(self.properties["untyped_items"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

        with context("with an untyped dict parameter"):
            with it("should advertise JSON Schema object"):
                expect(self.properties["untyped_fields"]).to(equal({"type": "object"}))

        with context("with a list of integers parameter"):
            with it("should advertise JSON Schema array of integer"):
                expect(self.properties["counted_items"]).to(
                    equal({"type": "array", "items": {"type": "integer"}})
                )

        with context("with a list of booleans parameter"):
            with it("should advertise JSON Schema array of boolean"):
                expect(self.properties["flagged_items"]).to(
                    equal({"type": "array", "items": {"type": "boolean"}})
                )

        with context("with a list of floats parameter"):
            with it("should advertise JSON Schema array of number"):
                expect(self.properties["measured_items"]).to(
                    equal({"type": "array", "items": {"type": "number"}})
                )

        with context("with a nested list parameter"):
            with it("should advertise JSON Schema array of array of string"):
                expect(self.properties["nested_items"]).to(
                    equal(
                        {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "string"}},
                        }
                    )
                )

        with context("with a list of dicts parameter"):
            with it("should advertise JSON Schema array of object with string additionalProperties"):
                expect(self.properties["record_items"]).to(
                    equal(
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                            },
                        }
                    )
                )

        with context("with a dict of integer values parameter"):
            with it("should advertise JSON Schema object with integer additionalProperties"):
                expect(self.properties["counted_fields"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        }
                    )
                )

        with context("with a dict of list values parameter"):
            with it("should advertise JSON Schema object with array additionalProperties"):
                expect(self.properties["listed_fields"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                        }
                    )
                )

        with context("with an optional string parameter"):
            with it("should advertise anyOf string and null"):
                expect(_sorted_any_of_types(self.properties["optional_text"])).to(
                    equal(["null", "string"])
                )

        with context("with an optional integer parameter"):
            with it("should advertise anyOf integer and null"):
                expect(_sorted_any_of_types(self.properties["optional_count"])).to(
                    equal(["integer", "null"])
                )

        with context("with an optional boolean parameter"):
            with it("should advertise anyOf boolean and null"):
                expect(_sorted_any_of_types(self.properties["optional_flag"])).to(
                    equal(["boolean", "null"])
                )

        with context("with an optional float parameter"):
            with it("should advertise anyOf number and null"):
                expect(_sorted_any_of_types(self.properties["optional_ratio"])).to(
                    equal(["null", "number"])
                )

        with context("with an optional list parameter"):
            with it("should advertise anyOf array and null"):
                expect(
                    sorted(
                        variant["type"]
                        for variant in self.properties["optional_items"]["anyOf"]
                    )
                ).to(equal(["array", "null"]))

        with context("with an optional dict parameter"):
            with it("should advertise anyOf object and null"):
                expect(
                    sorted(
                        variant["type"]
                        for variant in self.properties["optional_fields"]["anyOf"]
                    )
                ).to(equal(["null", "object"]))

        with context("with a string-or-integer union parameter"):
            with it("should advertise anyOf string and integer"):
                expect(_sorted_any_of_types(self.properties["text_or_count"])).to(
                    equal(["integer", "string"])
                )

        with context("with optional parameters that have defaults"):
            with it("should omit optional_text from required"):
                expect("optional_text" in self.schema["required"]).to(equal(False))

            with it("should still require text"):
                expect(self.schema["required"]).to(contain("text"))

            with it("should still require items"):
                expect(self.schema["required"]).to(contain("items"))

            with it("should still require fields"):
                expect(self.schema["required"]).to(contain("fields"))

            with it("should still require flag"):
                expect(self.schema["required"]).to(contain("flag"))

    with context("that has been derived from a ParameterTypes echo_sequence operation"):
        with context("with a Sequence of strings parameter"):
            with it("should advertise JSON Schema array of string"):
                schema = _input_schema_for_callable(ParameterTypes().echo_sequence)
                expect(schema["properties"]["value"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

    with context("that has been derived from a ParameterTypes echo_mapping operation"):
        with context("with a Mapping of integer values parameter"):
            with it("should advertise JSON Schema object with integer additionalProperties"):
                schema = _input_schema_for_callable(ParameterTypes().echo_mapping)
                expect(schema["properties"]["value"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        }
                    )
                )

    with context("that has been derived from a ParameterTypes echo_unannotated operation"):
        with context("with an unannotated parameter"):
            with it("should advertise JSON Schema string"):
                schema = _input_schema_for_callable(ParameterTypes().echo_unannotated)
                expect(schema["properties"]["value"]).to(equal({"type": "string"}))

    with context("that has been derived from iterate.iterate"):
        with context("with a tools list parameter"):
            with it("should advertise JSON Schema array of string"):
                schema = _input_schema_for_callable(Iterate.iterate)
                expect(schema["properties"]["tools"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )
