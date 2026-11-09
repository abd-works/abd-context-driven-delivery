class Practice:
    name: str
    folder: str
    fidelities: list

    def first_fidelity(self) -> str:
        return self.fidelities[0]


class Catalog:
    def __init__(self, practices: list[Practice]) -> None:
        self.practices = practices

    def first(self) -> Practice:
        return self.practices[0]
