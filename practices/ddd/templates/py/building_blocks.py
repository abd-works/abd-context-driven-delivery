# ---
# fidelity: building_blocks
# format: py
# ---
#
# One class per building block. Keep only the operations this type is allowed to have.
# {DomainName} is the aggregate or the concept the block is about.

class {DomainName}(Entity):
    """Identity stays the same when values change. Members change with it."""

    def __init__(self) -> None:
        self.identity = ""
        self.is_root = False


class {DomainName}Value:
    """No setters. create, clone, and mix each return a new instance."""

    def create(self) -> "{DomainName}Value":
        return {DomainName}Value()

    def clone(self) -> "{DomainName}Value":
        return {DomainName}Value()

    def mix(self, other: "{DomainName}Value") -> "{DomainName}Value":
        return {DomainName}Value()


class {DomainName}Repository:
    """A collection. Keep any of these. search may appear more than once; name it search plus what it searches."""

    def create(self, {domain_name}: {DomainName}) -> {DomainName}:
        ...

    def read(self, identity: str) -> {DomainName}:
        ...

    def update(self, {domain_name}: {DomainName}) -> {DomainName}:
        ...

    def delete(self, identity: str) -> None:
        ...

    def search_by_{criterion}(self, {criterion}: str) -> list[{DomainName}]:
        ...


class {DomainName}Service:
    """No state. The operation is one no domain object can perform."""

    def {operation}(self) -> None:
        ...


class {DomainName}{EventName}:
    """The subject is the state of the event."""

    def __init__(self) -> None:
        self.producer = None
        self.consumers = []
        self.subject = None


class {DomainName}Specification:
    """True when the candidate matches this rule."""

    def is_satisfied_by(self, candidate: {DomainName}) -> bool:
        ...


class {DomainName}Factory:
    """Builds the aggregate in a valid state."""

    def create(self) -> {DomainName}:
        ...
