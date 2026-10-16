"""Each given, when, and then shows a clean-engineering edge of its own."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph

_SAMPLE = _HERE / "examples" / "input"


def walk(node: dict):
    yield node
    for child in node.get("children") or []:
        yield from walk(child)


def named(node: dict, name: str, type: str) -> dict:
    for item in walk(node):
        if item.get("name") == name and item.get("type") == type:
            return item
    raise AssertionError(f"missing {type} {name}")


def child_names(node: dict, holder: str) -> list[str]:
    for child in node.get("children") or []:
        if child.get("name") == holder:
            return [item.get("name") for item in child.get("children") or []]
    return []


with description("a scenario"):
    with context("whose steps call the domain or name an example"):
        with before.all:
            graph = Graph()
            roots = {"clean_engineering": str(_SAMPLE), "stories": str(_SAMPLE)}
            graph.load_working_copy(str(_HERE), roots, database=str(_SAMPLE))
            self.scenario = named(
                graph.practice("stories").root_node.serialize(),
                "Enter validation code",
                "Scenario",
            )
            self.given = named(self.scenario, "given the User has submitted valid account credentials", "Given")
            self.when = named(self.scenario, "when the User verifies the account with the emailed validation code", "When")
            self.then = named(self.scenario, "then the account is verified", "Then")

        with it("should show the given through its example and the operation it calls"):
            example = named(self.given, "unverifiedAccountCredentials", "Example")
            expect(child_names(example, "demonstrates")).to(contain("AccountCredentials"))
            expect(child_names(self.given, "invokes")).to(equal(["register"]))

        with it("should show the when through its example and the operation it calls"):
            expect([child.get("name") for child in self.when.get("children") or []]).to(contain("emailedValidationCode"))
            expect(child_names(self.when, "invokes")).to(equal(["verify"]))

        with it("should show the then through the property it reads"):
            expect(child_names(self.then, "observes")).to(equal(["verified"]))
