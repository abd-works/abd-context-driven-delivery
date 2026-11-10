from __future__ import annotations







class Effect(Trait):
    @property
    def action(self) -> object:
        ...

    @property
    def range(self) -> object:
        ...

    @property
    def duration(self) -> object:
        ...

    @property
    def base_cost_per_rank(self) -> object:
        ...

    @property
    def resolve(self) -> object:
        ...
