"""The edges Clean Engineering reads between the classes of the code: the class each extends, the parts and collaborators
each holds, each class its operations create, call, or read, with how each reaches it, and each call joined to the one
operation its receiver's class gives it."""

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

# A car that extends a vehicle and reaches each other class of its garage one way: the engine it builds and keeps, the
# driver it is handed and keeps, the passengers it is handed as a list, a map it builds on each call, a pump handed to
# one operation, the driver's licence through the driver, a depot a class operation finds by name, the registry its
# module holds, and a wheel, a seat, and a mirror it only names as values. Five receivers' classes the code does not
# say: a horn whose operation one imported class alone declares, so the call is joined by a guess; a worker typed by a
# class of the standard library; a value nothing types; and a tank typed by a name no file declares; the last three
# each call an operation two imported classes declare.
_GARAGE = {
    "garage/wheel.py": "class Wheel:\n    size = 16\n",
    "garage/seat.py": "class Seat:\n    rows = 2\n",
    "garage/mirror.py": "class Mirror:\n    sides = 2\n",
    "garage/vehicle.py": "class Vehicle:\n    def __init__(self, name: str) -> None:\n        self.name = name\n",
    "garage/engine.py": "class Engine:\n    def start(self) -> int:\n        return 1\n",
    "garage/licence.py": "class Licence:\n    def check(self) -> bool:\n        return True\n",
    "garage/driver.py": (
        "from garage.licence import Licence\n\n\n"
        "class Driver:\n    def __init__(self, licence: Licence) -> None:\n        self.licence = licence\n"
    ),
    "garage/passenger.py": "class Passenger:\n    def board(self) -> bool:\n        return True\n",
    "garage/map.py": "class Map:\n    def route(self) -> str:\n        return 'north'\n",
    "garage/pump.py": (
        "class Pump:\n    def pour(self) -> int:\n        return 5\n\n"
        "    def start(self) -> int:\n        return 2\n"
    ),
    "garage/depot.py": (
        "class Depot:\n    def __init__(self, name: str) -> None:\n        self.name = name\n\n"
        "    @classmethod\n    def named(cls, name: str) -> 'Depot':\n        return cls(name)\n\n"
        "    def open(self) -> bool:\n        return True\n"
    ),
    "garage/registry.py": (
        "from garage.depot import Depot\n\n\n"
        "class Registry:\n    def find(self, name: str) -> Depot:\n        return Depot(name)\n\n\n"
        "REGISTRY = Registry()\n"
    ),
    "garage/car.py": (
        "from threading import Thread\n\n"
        "from garage.depot import Depot\n"
        "from garage.driver import Driver\n"
        "from garage.engine import Engine\n"
        "from garage.map import Map\n"
        "from garage.mirror import Mirror\n"
        "from garage.passenger import Passenger\n"
        "from garage.pump import Pump\n"
        "from garage.registry import REGISTRY\n"
        "from garage.seat import Seat\n"
        "from garage.vehicle import Vehicle\n"
        "from garage.wheel import Wheel\n\n\n"
        "class Car(Vehicle):\n"
        "    def __init__(self, name: str, driver: Driver, passengers: list[Passenger]) -> None:\n"
        "        super().__init__(name)\n"
        "        self.engine = Engine()\n"
        "        self.driver = driver\n"
        "        self.passengers = passengers\n\n"
        "    def drive(self) -> int:\n        return self.engine.start()\n\n"
        "    def plan(self) -> str:\n        return Map().route()\n\n"
        "    def fill(self, pump: Pump) -> int:\n        return pump.pour()\n\n"
        "    def check(self) -> bool:\n        return self.driver.licence.check()\n\n"
        "    def park(self) -> bool:\n        return Depot.named('north').open()\n\n"
        "    def store(self) -> bool:\n        return REGISTRY.find('south').open()\n\n"
        "    def is_wheel(self, thing: object) -> bool:\n        return isinstance(thing, Wheel)\n\n"
        "    def seats(self) -> list:\n        return [Seat]\n\n"
        "    def fits(self) -> bool:\n        return callable(Mirror)\n\n"
        "    def honk(self, horn) -> bool:\n        return horn.board()\n\n"
        "    def spin(self, worker: Thread) -> None:\n        worker.start()\n\n"
        "    def wander(self, somewhere) -> int:\n        return somewhere.start()\n\n"
        "    def refuel(self, tank: 'Tank') -> int:\n        return tank.start()\n"
    ),
}

# A truck in TypeScript that builds the engine it keeps and is handed the driver it keeps, and a bus that keeps the driver
# it is handed through a constructor parameter that declares the field.
_FLEET_SCRIPT = {
    "fleet/engine.ts": "export class Engine {\n  start(): number { return 1; }\n}\n",
    "fleet/driver.ts": "export class Driver {\n  wave(): boolean { return true; }\n}\n",
    "fleet/truck.ts": (
        "import { Engine } from './engine';\n"
        "import { Driver } from './driver';\n\n"
        "export class Truck {\n"
        "  private readonly engine = new Engine();\n"
        "  driver: Driver;\n"
        "  constructor(driver: Driver) { this.driver = driver; }\n"
        "  drive(): number { return this.engine.start(); }\n"
        "}\n"
    ),
    "fleet/bus.ts": (
        "import { Driver } from './driver';\n\n"
        "export class Bus {\n"
        "  constructor(private readonly driver: Driver) {}\n"
        "  greet(): boolean { return this.driver.wave(); }\n"
        "}\n"
    ),
}

# A van in JavaScript that builds the engine it keeps in its constructor.
_FLEET_JAVASCRIPT = {
    "van/engine.js": "export class Engine {\n  start() { return 1; }\n}\n",
    "van/van.js": (
        "import { Engine } from './engine.js';\n\n"
        "export class Van {\n"
        "  constructor() { this.engine = new Engine(); }\n"
        "  drive() { return this.engine.start(); }\n"
        "}\n"
    ),
}


def _classes_related(fixture, kind: str, source: str) -> list[str]:
    """The classes an edge of kind leads to from the class called source."""
    edges = fixture.practice.reading.in_graph.edge_index.of(kind)
    return sorted(edge.child.name for edge in edges if edge.parent.name == source and edge.parent.type == "OoadClass")


def _reached(fixture, source: str, target: str) -> list[str]:
    """Each way the class called source reaches the class called target, as its dependency edge keeps them."""
    edges = fixture.practice.reading.in_graph.edge_index.of("dependsOn")
    found = next((edge for edge in edges if edge.parent.name == source and edge.child.name == target), None)
    return sorted(found.facts.get("reached", [])) if found is not None else []


def _invoked(fixture, caller: str, owner: str) -> list[str]:
    """Each member the operation caller of the class owner invokes, as `Class.member`."""
    edges = fixture.practice.reading.in_graph.edge_index.of("invokes")
    return sorted(
        f"{edge.child.get_fact('owner')}.{edge.child.name}" for edge in edges
        if edge.parent.name == caller and edge.parent.get_fact("owner") == owner
    )


def _invoke_facts(fixture, caller: str, called: str) -> dict:
    """The facts the invokes edge from the operation caller to the member called, as `Class.member`, keeps."""
    edges = fixture.practice.reading.in_graph.edge_index.of("invokes")
    found = next(edge for edge in edges if edge.parent.name == caller and f"{edge.child.get_fact('owner')}.{edge.child.name}" == called)
    return dict(found.facts)


def _class_named(fixture, name: str):
    return next(node for node in fixture.practice.reading.in_graph.nodes("OoadClass") if node.name == name)


with description("the edges Clean Engineering reads between classes of the code"):
    with context("with Python classes"):
        with before.all:
            self.fixture = practice_from_files(_GARAGE)

        with context("that extend another"):
            with it("should join the class to the class it extends"):
                expect(_classes_related(self.fixture, "baseClass", "Car")).to(equal(["Vehicle"]))

        with context("that hold parts and collaborators in fields"):
            with it("should read the part the class builds and keeps as a composition"):
                expect(_classes_related(self.fixture, "composition", "Car")).to(equal(["Engine"]))

            with it("should read the collaborator the class is handed and keeps as an association"):
                expect(_classes_related(self.fixture, "association", "Car")).to(equal(["Driver"]))

            with it("should read the many members the class is handed and keeps as an aggregation"):
                expect(_classes_related(self.fixture, "aggregation", "Car")).to(equal(["Passenger"]))

        with context("that reach other classes from their operations"):
            with it("should depend on each class it creates, calls, or reads"):
                expect(_classes_related(self.fixture, "dependsOn", "Car")).to(
                    equal(["Depot", "Driver", "Engine", "Licence", "Map", "Mirror", "Passenger", "Pump", "Registry", "Seat", "Wheel"])
                )

            with it("should keep that it creates the part in its constructor and then calls it through the field that holds it"):
                expect(_reached(self.fixture, "Car", "Engine")).to(equal(["created in the constructor", "held as a field"]))

            with it("should keep that it creates a class on each call"):
                expect(_reached(self.fixture, "Car", "Map")).to(equal(["created on each call"]))

            with it("should keep that a class is handed in as a parameter"):
                expect(_reached(self.fixture, "Car", "Pump")).to(equal(["handed in as a parameter"]))

            with it("should keep that a class is reached through another object it holds"):
                expect(_reached(self.fixture, "Car", "Licence")).to(equal(["reached through another object"]))

            with it("should keep that a class is looked up by name"):
                expect(_reached(self.fixture, "Car", "Depot")).to(equal(["looked up by name"]))

            with it("should keep that a class is a module's object"):
                expect(_reached(self.fixture, "Car", "Registry")).to(equal(["a module's object"]))

            with it("should keep that a class an isinstance check names is named as a value"):
                expect(_reached(self.fixture, "Car", "Wheel")).to(equal(["named as a value"]))

            with it("should keep that a class a list holds is named as a value"):
                expect(_reached(self.fixture, "Car", "Seat")).to(equal(["named as a value"]))

            with it("should keep that a class handed to a call is named as a value"):
                expect(_reached(self.fixture, "Car", "Mirror")).to(equal(["named as a value"]))

            with it("should not read a class a type hint names as named as a value"):
                expect(_reached(self.fixture, "Car", "Passenger")).to(equal(["held as a field"]))

        with context("that call operations other classes declare under the same name"):
            with it("should join super().__init__ to the constructor of the class it extends alone"):
                expect(_invoked(self.fixture, "__init__", "Car")).to(equal(["Car.driver", "Car.engine", "Car.passengers", "Vehicle.__init__"]))

            with it("should join a call whose receiver's class the code does not say to nothing"):
                expect(_invoked(self.fixture, "wander", "Car")).to(equal([]))

            with it("should join a call to the one operation of that name the classes in reach declare, marked as joined by a guess"):
                expect(_invoke_facts(self.fixture, "honk", "Passenger.board")).to(equal({"joined": ["by a guess: one class in reach declares the name"]}))

            with it("should mark no call joined by its receiver's class"):
                expect(_invoke_facts(self.fixture, "fill", "Pump.pour")).to(equal({}))

            with it("should count on the class each call it could not join whose receiver is an object from outside the code"):
                expect(_class_named(self.fixture, "Car").get_fact("unresolved_calls_on_outside_objects")).to(equal(1))

            with it("should count on the class each call it could not join whose receiver no type says"):
                expect(_class_named(self.fixture, "Car").get_fact("unresolved_calls_on_untyped_values")).to(equal(1))

            with it("should count on the class each other call it could not join"):
                expect(_class_named(self.fixture, "Car").get_fact("unresolved_calls_otherwise")).to(equal(1))

    with context("with TypeScript classes"):
        with before.all:
            self.fixture = practice_from_files(_FLEET_SCRIPT)

        with it("should read the part the class builds in its field's initializer as a composition"):
            expect(_classes_related(self.fixture, "composition", "Truck")).to(equal(["Engine"]))

        with it("should read the collaborator the class is handed and keeps as an association"):
            expect(_classes_related(self.fixture, "association", "Truck")).to(equal(["Driver"]))

        with it("should keep that the class calls its part through the field that holds it"):
            expect(_reached(self.fixture, "Truck", "Engine")).to(equal(["created in the constructor", "held as a field"]))

        with it("should read the collaborator a constructor parameter declares as a field as an association"):
            expect(_classes_related(self.fixture, "association", "Bus")).to(equal(["Driver"]))

        with it("should keep that the class calls the collaborator through the field its constructor parameter declares"):
            expect(_reached(self.fixture, "Bus", "Driver")).to(equal(["held as a field"]))

    with context("with JavaScript classes"):
        with before.all:
            self.fixture = practice_from_files(_FLEET_JAVASCRIPT)

        with it("should read the part the class builds in its constructor as a composition"):
            expect(_classes_related(self.fixture, "composition", "Van")).to(equal(["Engine"]))

        with it("should keep that the class creates its part in the constructor and calls it through the field"):
            expect(_reached(self.fixture, "Van", "Engine")).to(equal(["created in the constructor", "held as a field"]))
