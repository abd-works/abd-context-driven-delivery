from __future__ import annotations







class GradedCheckResult(CheckResult):
    @property
    def degree(self) -> object:
        ...

    @property
    def resulting_condition(self) -> object:
        ...
