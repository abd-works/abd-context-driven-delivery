"""The arguments an operation's body hands each call it makes by name, read from its text: what two facts across files
compare, the values a class builds another from and the parameters an operation hands on."""

from __future__ import annotations

import re

from cdd_guidance.practices.source_code import BracketStructure, split_top_level


class CallArguments:
    """<<Value Object>> The body of one operation, read for the calls it makes."""

    def __init__(self, body: str) -> None:
        self._body = body

    def of(self, callee: str) -> list[list[str]]:
        """Each call of callee the body makes, as its arguments in order, each as written: `Map("north", **places)`
        gives ``["\\"north\\"", "**places"]``. A call of a name that only ends in callee, such as `make_map(` for `map`,
        is not one."""
        calls: list[list[str]] = []
        for found in re.finditer(rf"(?<![\w$]){re.escape(callee)}\s*\(", self._body):
            opened = found.end() - 1
            closed = BracketStructure(self._body).closing_bracket(opened, "(", ")")
            if closed is not None:
                calls.append(split_top_level(self._body[opened + 1 : closed]))
        return calls
