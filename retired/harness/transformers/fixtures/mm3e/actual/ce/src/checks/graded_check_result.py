from __future__ import annotations

from .check_result import CheckResult

class GradedCheckResult(CheckResult):




    @property
    def degree(self) -> object:
        ...


    @property
    def resulting_condition(self) -> object:
        ...
