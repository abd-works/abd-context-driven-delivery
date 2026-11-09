"""Operation body metrics used by graph rules."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.operation_metrics import SourceText
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel


def _parsed_operation(method: str) -> Operation:
    """The one method of an `Account` class, read as the TypeScript parser reads it."""
    model = TypeScriptCleanEngineeringModel().parse(f"export class Account {{\n  {method}\n}}\n")
    return model.file_module().classes[0].operations[0]


with description("peer private access in operation bodies"):
    with it("should ignore this._field and self._field on the same object"):
        expect(SourceText("this._email = email;").reaches_peer_private()).to(equal(False))
        expect(SourceText("return self._total;").reaches_peer_private()).to(equal(False))

    with it("should flag another receiver's _field"):
        expect(SourceText("return peer._secret;").reaches_peer_private()).to(equal(True))

    with it("should ignore aggregate _repository wiring from a repository"):
        expect(SourceText("customerProfile._repository = this;").reaches_peer_private()).to(equal(False))

    with it("should ignore same-type field copy from a method parameter"):
        body = "this._plan = source._plan;\nthis.simType = source.simType;"
        expect(SourceText(body).reaches_peer_private()).to(equal(False))

    with it("should still flag reading a parameter private field without copying to this"):
        body = "return source._plan;"
        expect(SourceText(body).reaches_peer_private()).to(equal(True))

    with it("should set peer_private_access on a parsed operation that reads another object's private member"):
        expect(_parsed_operation("run(other: Order) { return other._state; }").peer_private_access).to(equal(True))

    with it("should read the class that holds a parsed operation as its own, without being told its name"):
        expect(_parsed_operation("merge(other: Account) { return other._email; }").peer_private_access).to(equal(False))

    with it("should read an object a parsed operation builds of its own class as its own"):
        body = "copy() { const made = new Account(); made._email = this._email; return made; }"
        expect(_parsed_operation(body).peer_private_access).to(equal(False))
