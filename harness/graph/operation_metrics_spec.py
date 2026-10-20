"""Operation body metrics used by graph rules."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.operation_metrics import (
    apply_brace_body_metrics,
    peer_private_access_in_text,
)


with description("peer private access in operation bodies"):
    with it("should ignore this._field and self._field on the same object"):
        expect(peer_private_access_in_text("this._email = email;")).to(equal(False))
        expect(peer_private_access_in_text("return self._total;")).to(equal(False))

    with it("should flag another receiver's _field"):
        expect(peer_private_access_in_text("return peer._secret;")).to(equal(True))

    with it("should ignore aggregate _repository wiring from a repository"):
        expect(peer_private_access_in_text("customerProfile._repository = this;")).to(equal(False))

    with it("should set peer_private_access on parsed operations"):
        own = Operation("constructor", 1)
        apply_brace_body_metrics(own, "this._email = email;\nthis._password = password;")
        expect(own.peer_private_access).to(equal(False))
        cross = Operation("run", 2)
        apply_brace_body_metrics(cross, "other._state = value;")
        expect(cross.peer_private_access).to(equal(True))
