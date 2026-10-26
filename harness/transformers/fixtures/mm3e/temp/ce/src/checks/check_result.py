from __future__ import annotations



class CheckResult:
    @property
    def roll_total(self) -> object:
        ...

    @property
    def dc(self) -> object:
        ...

    @property
    def is_success(self) -> object:
        ...

    @property
    def margin(self) -> object:
        ...

    @property
    def is_critical(self) -> object:
        ...
