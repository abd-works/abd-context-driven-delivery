"""Operation body metrics used by graph rules."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import ast

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.operation_metrics import PythonFunctionBody
from cdd_guidance.practices.source_code import SourceText
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel


def _parsed_operation(method: str) -> Operation:
    """The one method of an `Account` class, read as the TypeScript parser reads it."""
    model = TypeScriptCleanEngineeringModel().parse(f"export class Account {{\n  {method}\n}}\n")
    return model.file_module().classes[0].operations[0]


with description("peer private access in operation bodies"):
    with it("should ignore this._field and self._field on the same object"):
        expect(SourceText("this._email = email;").collaborators.reaches_peer_private()).to(equal(False))
        expect(SourceText("return self._total;").collaborators.reaches_peer_private()).to(equal(False))

    with it("should flag another receiver's _field"):
        expect(SourceText("return peer._secret;").collaborators.reaches_peer_private()).to(equal(True))

    with it("should ignore aggregate _repository wiring from a repository"):
        expect(SourceText("customerProfile._repository = this;").collaborators.reaches_peer_private()).to(equal(False))

    with it("should ignore same-type field copy from a method parameter"):
        body = "this._plan = source._plan;\nthis.simType = source.simType;"
        expect(SourceText(body).collaborators.reaches_peer_private()).to(equal(False))

    with it("should still flag reading a parameter private field without copying to this"):
        body = "return source._plan;"
        expect(SourceText(body).collaborators.reaches_peer_private()).to(equal(True))

    with it("should set peer_private_access on a parsed operation that reads another object's private member"):
        expect(_parsed_operation("run(other: Order) { return other._state; }").peer_private_access).to(equal(True))

    with it("should read the class that holds a parsed operation as its own, without being told its name"):
        expect(_parsed_operation("merge(other: Account) { return other._email; }").peer_private_access).to(equal(False))

    with it("should read an object a parsed operation builds of its own class as its own"):
        body = "copy() { const made = new Account(); made._email = this._email; return made; }"
        expect(_parsed_operation(body).peer_private_access).to(equal(False))


def _python_body(source: str) -> PythonFunctionBody:
    """The one function of source, read from its syntax tree as the Python parser reads a module function."""
    return PythonFunctionBody(ast.parse(source).body[0], None)


with description("a measured body, as a span of any language and as a Python function"):
    with context("that catches every failure and drops it"):
        with before.all:
            self.bodies = [
                SourceText("try { run(); } catch () { return null; }"),
                _python_body("def run():\n    try:\n        go()\n    except:\n        pass\n"),
            ]

        with it("should say each catches everything"):
            expect([body.catches_everything() for body in self.bodies]).to(equal([True, True]))

        with it("should say each swallows what it caught"):
            expect([body.swallows() for body in self.bodies]).to(equal([True, True]))

    with context("that catches a named failure and raises it again"):
        with before.all:
            self.bodies = [
                SourceText("try { run(); } catch (error) { throw error; }"),
                _python_body("def run():\n    try:\n        go()\n    except KeyError:\n        raise\n"),
            ]

        with it("should say neither catches everything"):
            expect([body.catches_everything() for body in self.bodies]).to(equal([False, False]))

        with it("should say neither swallows what it caught"):
            expect([body.swallows() for body in self.bodies]).to(equal([False, False]))


with description("descriptive comments in a span"):
    with it("should read a // comment that carries narrative as a descriptive comment"):
        expect(SourceText("total = 1  // see also the cart's implementation").has_prose_comment()).to(equal(True))

    with it("should not read a // inside a string literal as a comment"):
        line = '"  // A view carries the state an operation returned; the implementation unsubscribes.",'
        expect(SourceText(line).has_prose_comment()).to(equal(False))
