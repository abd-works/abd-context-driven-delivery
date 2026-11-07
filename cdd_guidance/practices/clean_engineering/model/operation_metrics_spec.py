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
        expect(SourceText(body).reaches_peer_private(frozenset({"source"}))).to(equal(False))

    with it("should still flag reading a parameter private field without copying to this"):
        body = "return source._plan;"
        expect(SourceText(body).reaches_peer_private(frozenset({"source"}))).to(equal(True))

    with it("should set peer_private_access on parsed operations"):
        own = Operation("constructor", 1)
        own.load_brace_body_facts("this._email = email;\nthis._password = password;")
        expect(own.peer_private_access).to(equal(False))
        cross = Operation("run", 2)
        cross.load_brace_body_facts("other._state = value;")
        expect(cross.peer_private_access).to(equal(True))
