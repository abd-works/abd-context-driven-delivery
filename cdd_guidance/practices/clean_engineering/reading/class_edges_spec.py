"""The edges Clean Engineering reads between the classes of the code: the class each extends, the parts and collaborators
each holds, each class its operations create, call, or read, with how each reaches it, and each call joined to the one
operation its receiver's class gives it."""

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

# A car that extends a vehicle and reaches each other class of its garage one way: the engine it builds and keeps, the
# driver it is handed and keeps, the passengers it is handed as a list, a map it builds on each call, a pump handed to
# one operation, the driver's licence through the driver, a depot a class operation finds by name, the registry its
# module holds, and a wheel, a seat, and a mirror it only names as values. Five receivers' classes the code does not
# say: a horn whose operation one imported class alone declares, so the call is joined by a guess; a worker typed by a
# class of the standard library; a value nothing types; and a tank typed by a name no file declares; the last three
# each call an operation two imported classes declare; and three built-in objects the code assigns with no hint, a match
# a module's compiled pattern answers, a list it writes, and a list a field holds, whose operations two classes declare.
_GARAGE = {
    "garage/wheel.py": "class Wheel:\n    size = 16\n",
    "garage/seat.py": "class Seat:\n    rows = 2\n",
    "garage/mirror.py": "class Mirror:\n    sides = 2\n",
    "garage/no_plate.py": "class NoPlate(Exception):\n    pass\n",
    "garage/__init__.py": "from garage.registry import REGISTRY\n\nREGISTRY.find('north')\n",
    "garage/glovebox.py": (
        "class Manual:\n    def read(self) -> str:\n        return 'manual'\n\n\n"
        "class Glovebox:\n    def __init__(self) -> None:\n        self._start()\n\n    def _start(self) -> None:\n        self.manual = Manual()\n\n\n"
        "class Trunk(Glovebox):\n    size = 1\n\n\n"
        "class SmallTrunk(Trunk):\n    size = 2\n\n\n"
        "class Dashboard:\n    def __init__(self, boxes: list[Glovebox]) -> None:\n        self.boxes = boxes\n\n    def read_all(self) -> list:\n        return [box.manual.read() for box in self.boxes]\n\n    def trunk_manual(self, trunk: SmallTrunk) -> str:\n        return trunk.manual.read()\n"
    ),
    "garage/shelving.py": (
        "from typing import Generic, Iterator, TypeVar\n\n"
        "Item = TypeVar('Item')\n\n\n"
        "class Shelving(Generic[Item]):\n    def __init__(self, items: list[Item]) -> None:\n        self._items = items\n\n"
        "    def __iter__(self) -> Iterator[Item]:\n        return iter(self._items)\n\n"
        "    def first(self) -> Item:\n        return self._items[0]\n\n"
        "    @property\n    def stock(self) -> tuple[Item, ...]:\n        return tuple(self._items)\n\n\n"
        "class Spanner:\n    def turn(self) -> int:\n        return 1\n\n\n"
        "class Wrench:\n    def turn(self) -> int:\n        return 2\n\n\n"
        "class ToolShelf(Shelving[\"Spanner\"]):\n    def count(self) -> int:\n        return 1\n\n\n"
        "class Workshop:\n    def __init__(self, shelf: ToolShelf) -> None:\n        self.shelf = shelf\n\n"
        "    def turn_all(self) -> list:\n        return [tool.turn() for tool in self.shelf]\n\n"
        "    def turn_first(self) -> int:\n        return self.shelf.first().turn()\n\n\n"
        "class WrenchRack:\n    def __init__(self, rack: Shelving[Wrench]) -> None:\n        self.rack = rack\n\n"
        "    def turn_one(self) -> int:\n        return self.rack.first().turn()\n\n"
        "    def turn_stock(self) -> list:\n        return [tool.turn() for tool in self.rack.stock]\n"
    ),
    "garage/parts/__init__.py": "from .bolts import *  # noqa: F403\n",
    "garage/parts/bolts.py": "class Bolt:\n    def tighten(self) -> int:\n        return 1\n",
    "garage/crane.py": (
        "class Polisher:\n    def buff(self) -> str:\n        return 'plain'\n\n\n"
        "class WaxPolisher(Polisher):\n    def buff(self) -> str:\n        return 'wax'\n\n\n"
        "class Named:\n    def title(self) -> str:\n        return 'crane'\n\n\n"
        "class Mover:\n    def move(self) -> int:\n        return 1\n\n\n"
        "class Ordered:\n    def move(self) -> int:\n        return super().move() + 1\n\n\n"
        "class Hoist(Ordered, Mover):\n    size = 1\n\n\n"
        "class Buffing:\n    def buff_all(self) -> str:\n        return self.pad.buff()\n\n\n"
        "class Buffer(Buffing):\n    pad_type: type[Polisher] = Polisher\n\n    def __init__(self) -> None:\n        self.pad = WaxPolisher()\n\n"
        "    def fresh(self) -> str:\n        return self.pad_type().buff()\n\n"
        "    def pad_kind(self) -> type[Polisher]:\n        return Polisher\n\n"
        "    def made(self) -> str:\n        return self.pad_kind()().buff()\n\n"
        "    def fresh_all(self, kinds: list[type[Polisher]]) -> list:\n        return [kind().buff() for kind in kinds]\n\n\n"
        "class Crane(Named, Mover):\n    def move(self) -> int:\n        return super().move()\n\n"
        "    def polisher(self) -> Polisher:\n        return WaxPolisher()\n\n"
        "    def shine_up(self) -> str:\n        return self.polisher().buff()\n\n"
        "    def buffing(self) -> object:\n        return self.polisher().buff if self else None\n"
    ),
    "garage/wiper.py": "class Wiper:\n    def record(self) -> None:\n        self.done = True\n",
    "garage/wash.py": (
        "from typing import Protocol\n\n\n"
        "class Washer(Protocol):\n    foam: str\n\n    def soap(self) -> str: ...\n\n    def rinse(self) -> str: ...\n\n\n"
        "class Hose:\n    foam = 'thick'\n\n    def soap(self) -> str:\n        return 'soap'\n\n    def rinse(self) -> str:\n        return 'rinse'\n\n\n"
        "class Bucket:\n    foam: str = 'thin'\n\n    def soap(self) -> str:\n        return 'foam'\n\n    def rinse(self) -> str:\n        return 'water'\n\n\n"
        "class Sponge:\n    def soap(self) -> str:\n        return 'soft'\n"
    ),
    "garage/polish.py": "def shine() -> str:\n    return 'shine'\n\n\ndef wax() -> str:\n    return 'wax'\n",
    "garage/fleet.py": (
        "from garage.engine import Engine\n\n\n"
        "class _Probe:\n    def __init__(self, error: object) -> None:\n        self.error = error\n\n"
        "    @property\n    def ready(self) -> bool:\n        return self.error is None\n\n\n"
        "def _engines() -> list:\n    return [Engine()]\n\n\n"
        "def _report() -> None:\n    print('report')\n\n\n"
        "ENGINES = _engines()\n\n"
        "if __name__ == '__main__':\n    _report()\n    print(_Probe(None).ready)\n"
    ),
    "garage/shelf.py": (
        "from typing import List\n\n\n"
        "class Registered(type):\n    pass\n\n\n"
        "class Tray:\n    size = 1\n\n    def measure(self) -> int:\n        return self.size\n\n\n"
        "class Bulb:\n    watts = 5\n\n    def measure(self) -> int:\n        return self.watts\n\n\n"
        "class Rack:\n    def __init__(self) -> None:\n        self._trays: list[Tray] = []\n\n"
        "    @property\n    def trays(self) -> List[\"Tray\"]:\n        return self._trays\n\n"
        "    @trays.setter\n    def trays(self, trays: List[\"Tray\"]) -> None:\n        self._trays = trays\n\n"
        "    def sizes(self) -> list:\n        return [tray.measure() for tray in self.trays]\n\n\n"
        "class Shelf(metaclass=Registered):\n    tray = Tray()\n\n"
        "    @property\n    def _bulb(self) -> Bulb:\n        return Bulb()\n\n"
        "    def show(self) -> bool:\n        return self._bulb is not None\n"
    ),
    "garage/inspection.py": (
        "class Inspection:\n    def record(self) -> None:\n        raise NotImplementedError\n\n\n"
        "class Brakes(Inspection):\n    def record(self) -> None:\n        self.done = True\n\n"
        "    @classmethod\n    def label(cls, name: str) -> str:\n        return name\n\n\n"
        "class Lights(Inspection):\n    def record(self) -> None:\n        self.done = True\n\n"
        "    @classmethod\n    def label(cls, name: str) -> str:\n        return name\n\n\n"
        "class Tyres(Inspection):\n    def record(self) -> None:\n        self.done = True\n"
    ),
    "garage/opener.py": (
        "class Remote:\n    def __init__(self, opener) -> None:\n        self.opener = opener\n\n"
        "    def press(self) -> bool:\n        return True\n\n\n"
        "class Opener:\n    def __init__(self, name: str) -> None:\n        self.remote = Remote(self)\n\n"
        "    @classmethod\n    def load(cls, name: str) -> Opener:\n        return cls(name)\n"
    ),
    "garage/vehicle.py": "class Vehicle:\n    def __init__(self, name: str) -> None:\n        self.name = name\n\n    def label(self) -> str:\n        return self.kind()\n\n    def kind(self) -> str:\n        return 'vehicle'\n",
    "garage/engine.py": "class Engine:\n    def start(self) -> int:\n        return 1\n\n    def count(self) -> int:\n        return 4\n",
    "garage/licence.py": "class Licence:\n    def check(self) -> bool:\n        return True\n",
    "garage/driver.py": (
        "from garage.licence import Licence\n\n\n"
        "class Driver:\n    def __init__(self, licence: Licence) -> None:\n        self.licence = licence\n"
    ),
    "garage/passenger.py": "class Passenger:\n    def board(self) -> bool:\n        return True\n",
    "garage/map.py": "class Map:\n    def route(self) -> str:\n        return 'north'\n",
    "garage/pump.py": (
        "class Pump:\n    def pour(self) -> int:\n        return 5\n\n"
        "    def start(self) -> int:\n        return 2\n\n"
        "    def count(self) -> int:\n        return 1\n"
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
        "import re\nfrom threading import Thread\n\n"
        "from garage.depot import Depot\n"
        "from garage.driver import Driver\n"
        "from garage.engine import Engine\n"
        "from garage.inspection import Brakes, Inspection, Lights\n"
        "from garage.map import Map\n"
        "from garage.mirror import Mirror\n"
        "from garage.no_plate import NoPlate\n"
        "from garage.opener import Opener\n"
        "from garage import polish\n"
        "from garage.parts import Bolt\n"
        "from garage.wash import Washer\n"
        "from garage.passenger import Passenger\n"
        "from garage.pump import Pump\n"
        "from garage.registry import REGISTRY\n"
        "from garage.seat import Seat\n"
        "from garage.vehicle import Vehicle\n"
        "from garage.wiper import Wiper\n"
        "from garage.wheel import Wheel\n\n"
        "_PLATE = re.compile('[A-Z]+')\n\n\n"
        "def _odometer(item: object) -> int:\n    return 0\n\n\n"
        "class Car(Vehicle):\n"
        "    def __init__(self, name: str, driver: Driver, passengers: list[Passenger]) -> None:\n"
        "        super().__init__(name)\n"
        "        self.engine = Engine()\n"
        "        self.driver = driver\n"
        "        self.passengers = passengers\n"
        "        self.log = []\n\n"
        "    def started(self, cls: Pump) -> int:\n        return cls.pour()\n\n"
        "    def tidy(self, part: Brakes | Lights) -> None:\n        part.record()\n\n"
        "    @property\n    def _badge(self) -> str:\n        return 'b'\n\n"
        "    def describe(self) -> str:\n        return f\"\"\"<b>{self._badge}</b>\"\"\"\n\n"
        "    def fix(self, bolt: Bolt) -> int:\n        return bolt.tighten()\n\n"
        "    def wiped(self, checks: list[Inspection]) -> list:\n        made = [Wiper() for check in checks]\n        return [check for check in made if check.record()]\n\n"
        "    def kind(self) -> str:\n        return 'car'\n\n"
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
        "    def refuel(self, tank: 'Tank') -> int:\n        return tank.start()\n\n"
        "    def mark(self) -> int:\n        plate = _PLATE.search(self.name)\n        return plate.start()\n\n"
        "    def tally(self) -> int:\n        counts = [1, 2]\n        return counts.count(1)\n\n"
        "    def noted(self) -> int:\n        return self.log.count(1)\n\n"
        "    @property\n    def plate(self) -> str:\n        if not self.name:\n            raise NoPlate(self.name)\n        return self.name\n\n"
        "    def inspect(self) -> None:\n        for check in (Brakes(), Lights()):\n            check.record()\n\n"
        "    def buff(self) -> str:\n        return polish.shine()\n\n"
        "    def schedule(self) -> list:\n        return sorted([], key=_odometer)\n\n"
        "    def hooks(self) -> list:\n        return [self.drive, polish.wax]\n\n"
        "    def service(self) -> None:\n        for job in (\n            Brakes(),\n            Wiper(),\n        ):\n            job.record()\n\n"
        "    @staticmethod\n    def first_check(name: str) -> str:\n        kind = next((kind for kind in (Brakes, Lights) if kind.__name__ == name), None)\n        return kind.label(name)\n\n"
        "    def wash(self, washer: Washer) -> str:\n        return washer.soap()\n\n"
        "    def record_all(self, checks: dict[str, Inspection]) -> None:\n        for name, check in checks.items():\n            check.record()\n\n"
        "    def recheck_all(self, checks: dict[str, Inspection]) -> None:\n        for name, check in list(checks.items()):\n            check.record()\n\n"
        "    def check_any(self, found: object) -> None:\n        if not isinstance(found, Brakes):\n            return\n        found.record()\n\n"
        "    def check_one(self, checks: dict[str, Inspection]) -> None:\n        found = checks.get('brakes')\n        if found is None:\n            return\n        found.record()\n\n"
        "    def check_typed(self, found: Inspection) -> None:\n        if not isinstance(found, Brakes):\n            return\n        found.record()\n\n"
        "    def plates(self, drivers: list[Driver]) -> list:\n        licences = [driver.licence for driver in drivers]\n        return [licence.check() for licence in licences]\n\n"
        "    def all_records(self, checks: list[Inspection]) -> list:\n        return [done for check in checks for done in check.record()]\n\n"
        "    def kept_records(self, checks: list[Inspection]) -> None:\n        for check in [check for check in checks if check] or checks:\n            check.record()\n\n"
        "    def inspect_all(self, checks: list[Inspection]) -> None:\n        for check in checks:\n            check.record()\n\n"
        "    @property\n    def garage_open(self) -> bool:\n        return Opener.load('home').remote.press()\n"
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

# A page in TSX that renders a class component and a function component as elements, and a view that renders the
# class component from an operation of its own.
_SHELL = {
    "shell/boundary.tsx": (
        "import { Component, ReactNode } from 'react';\n\n"
        "export class Boundary extends Component<{ children: ReactNode }> {\n"
        "  render(): ReactNode { return this.props.children; }\n"
        "}\n"
    ),
    "shell/banner.tsx": "export function Banner() {\n  return <div>open</div>;\n}\n",
    "shell/start.ts": "export function boot(): void {\n  document.title = 'shell';\n}\n\nboot();\n",
    "shell/status.ts": (
        "export class Status {\n  failed(reason: string): void {\n    console.log(reason);\n  }\n}\n\n"
        "export class Alarm {\n  failed(reason: string): void {\n    console.log(reason);\n  }\n}\n"
    ),
    "shell/filter.ts": (
        "import { Status } from './status';\n\n"
        "interface FilterState {\n  status: Status;\n  label: string;\n}\n\n"
        "export class Filter {\n  constructor(private readonly state: FilterState) {}\n\n"
        "  change(): void {\n    this.state.status.failed('changed');\n  }\n}\n"
    ),
    "shell/marks.ts": (
        "function commentMarks(): string[] {\n  return ['comment'];\n}\n\n"
        "function changeMarks(): string[] {\n  return ['change'];\n}\n\n"
        "export function allMarks(): string[] {\n  return [...changeMarks(), ...commentMarks()];\n}\n\n"
        "export class Marks {\n  list(): string[] {\n    return [...this.extra()];\n  }\n\n  extra(): string[] {\n    return [];\n  }\n}\n"
    ),
    "shell/folds.js": (
        "function foldAt(line) {\n  return line;\n}\n\n"
        "export function foldAll(lines) {\n  return lines.map(foldAt.bind(null));\n}\n"
    ),
    "shell/label.ts": (
        "const markShown = (found: string): string => found;\n\n"
        "export function labelOf(text: string): string {\n  return `<b>${text.replace('x', markShown)}</b>`;\n}\n"
    ),
    "shell/page.tsx": (
        "import { Boundary } from './boundary';\n"
        "import { Banner } from './banner';\n\n"
        "export function Page() {\n"
        "  return (\n    <Boundary>\n      <Banner />\n    </Boundary>\n  );\n"
        "}\n"
    ),
    "shell/view.tsx": (
        "import { Boundary } from './boundary';\n\n"
        "export class View {\n"
        "  show() { return <Boundary>shown</Boundary>; }\n"
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


def _invoked_by_folder(fixture, folder: str) -> list[str]:
    """Each member the statements of the files the folder called folder holds invoke, as `Class.member`."""
    edges = fixture.practice.reading.in_graph.edge_index.of("invokes")
    return sorted(f"{edge.child.get_fact('owner')}.{edge.child.name}" for edge in edges if edge.parent.name == folder and edge.parent.type in ("Module", "Package"))


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
                    equal(["Bolt", "Brakes", "Depot", "Driver", "Engine", "Inspection", "Licence", "Lights", "Map", "Mirror", "NoPlate", "Opener", "Passenger", "Pump", "Registry", "Remote", "Seat", "Washer", "Wheel", "Wiper"])
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

            with it("should keep that a property's getter creates the failure it raises"):
                expect(_reached(self.fixture, "Car", "NoPlate")).to(equal(["created on each call"]))

            with it("should not read a class a type hint names as named as a value"):
                expect(_reached(self.fixture, "Car", "Passenger")).to(equal(["held as a field"]))

        with context("that are used outside any member"):
            with it("should join a call a module's own statements make, as made by the folder that holds it"):
                expect(_invoked_by_folder(self.fixture, "garage")).to(contain("_module._engines"))

            with it("should join a call an `if __name__` block makes, as made by the folder that holds it"):
                expect(_invoked_by_folder(self.fixture, "garage")).to(contain("_module._report"))

            with it("should join a call a package's own statements make on a module's object"):
                expect(_invoked_by_folder(self.fixture, "garage")).to(contain("Registry.find"))

            with it("should join a member a module's statement reads on an object it builds in place"):
                expect(_invoked_by_folder(self.fixture, "garage")).to(contain("_Probe.ready"))

            with it("should read a property that has a setter as what its getter answers"):
                expect(_invoked(self.fixture, "sizes", "Rack")).to(equal(["Rack.trays", "Tray.measure"]))

            with it("should keep that a class names its metaclass as a value"):
                expect(_reached(self.fixture, "Shelf", "Registered")).to(equal(["named as a value"]))

            with it("should keep that a class attribute's initializer creates its value with the class"):
                expect(_reached(self.fixture, "Shelf", "Tray")).to(equal(["created with the class"]))

            with it("should keep that a private property's getter creates what it answers on each call"):
                expect(_reached(self.fixture, "Shelf", "Bulb")).to(equal(["created on each call"]))

        with context("that call operations other classes declare under the same name"):
            with it("should join super().__init__ to the constructor of the class it extends alone"):
                expect(_invoked(self.fixture, "__init__", "Car")).to(equal(["Car.driver", "Car.engine", "Car.log", "Car.passengers", "Vehicle.__init__"]))

            with it("should join a call whose receiver's class the code does not say to nothing"):
                expect(_invoked(self.fixture, "wander", "Car")).to(equal([]))

            with it("should join a call to the one operation of that name the classes in reach declare, marked as joined by a guess"):
                expect(_invoke_facts(self.fixture, "honk", "Passenger.board")).to(equal({"joined": ["by a guess: one class in reach declares the name"]}))

            with it("should join a call on each item of a list it writes to the operation of every class the items are"):
                expect(_invoked(self.fixture, "inspect", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record"]))

            with it("should join a call on each item of a list of classes that share no base to the operation of each"):
                expect(_invoked(self.fixture, "service", "Car")).to(equal(["Brakes.record", "Wiper.record"]))

            with it("should join a call on a class taken from a list of classes to the operation each of them declares"):
                expect(_invoked(self.fixture, "first_check", "Car")).to(equal(["Brakes.label", "Lights.label"]))
            with it("should join a class to a protocol whose members it declares, and not one that declares only some"):
                expect(sorted(edge.parent.name for edge in self.fixture.practice.reading.in_graph.edge_index.of("realizes"))).to(equal(["Bucket", "Hose"]))

            with it("should join a call through a protocol to the operation of every class that satisfies it"):
                expect(_invoked(self.fixture, "wash", "Car")).to(equal(["Bucket.soap", "Hose.soap", "Washer.soap"]))
            with it("should join a call on the value a loop takes from a copy of a mapping's items"):
                expect(_invoked(self.fixture, "recheck_all", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record", "Tyres.record"]))
            with it("should join a call on a value an isinstance check has narrowed to one class"):
                expect(_invoked(self.fixture, "check_any", "Car")).to(equal(["Brakes.record"]))
            with it("should join a call on a value a mapping's get looks up"):
                expect(_invoked(self.fixture, "check_one", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record", "Tyres.record"]))
            with it("should join a call on a typed value an isinstance check has narrowed to a class extending its type"):
                expect(_invoked(self.fixture, "check_typed", "Car")).to(equal(["Brakes.record"]))
            with it("should join a call on the value a loop takes in two names from a mapping's items"):
                expect(_invoked(self.fixture, "record_all", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record", "Tyres.record"]))

            with it("should join a call on each item of a list a comprehension builds from another list's items"):
                expect(_invoked(self.fixture, "plates", "Car")).to(equal(["Driver.licence", "Licence.check"]))

            with it("should join a call through a field a method the constructor calls assigns"):
                expect(_invoked(self.fixture, "read_all", "Dashboard")).to(equal(["Dashboard.boxes", "Manual.read"]))

            with it("should join a call a class makes on itself to the operation each class extending it overrides"):
                expect(_invoked(self.fixture, "label", "Vehicle")).to(equal(["Car.kind", "Vehicle.kind"]))

            with it("should read a parameter named cls as the class its hint names, not the object itself"):
                expect(_invoked(self.fixture, "started", "Car")).to(equal(["Pump.pour"]))

            with it("should join a call on a value a union of classes types to the operation of each"):
                expect(_invoked(self.fixture, "tidy", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record"]))

            with it("should join a member a triple-quoted f-string reads"):
                expect(_invoked(self.fixture, "describe", "Car")).to(equal(["Car._badge"]))

            with it("should join a call through a field a class two levels up assigns"):
                expect(_invoked(self.fixture, "trunk_manual", "Dashboard")).to(equal(["Manual.read"]))

            with it("should take each item of a class that specialises a generic base as the class it names"):
                expect(_invoked(self.fixture, "turn_all", "Workshop")).to(equal(["Spanner.turn", "Workshop.shelf"]))

            with it("should take what a generic base's operation answers as the class the specialising class names"):
                expect(_invoked(self.fixture, "turn_first", "Workshop")).to(equal(["Shelving.first", "Spanner.turn", "Workshop.shelf"]))

            with it("should find a class a package passes on through a star import"):
                expect(_invoked(self.fixture, "fix", "Car")).to(equal(["Bolt.tighten"]))

            with it("should join a call on a value a class types to the operation each class extending it overrides"):
                expect(_invoked(self.fixture, "shine_up", "Crane")).to(equal(["Crane.polisher", "Polisher.buff", "WaxPolisher.buff"]))

            with it("should join super() to the operation of whichever base declares it"):
                expect(_invoked(self.fixture, "move", "Crane")).to(equal(["Mover.move"]))

            with it("should join a call on a field a mixin reads that the class mixing it in holds"):
                expect(_invoked(self.fixture, "buff_all", "Buffing")).to(equal(["Buffer.pad", "WaxPolisher.buff"]))

            with it("should join an operation another object's class declares that the code reads to hand on, and each override of it"):
                expect(_invoked(self.fixture, "buffing", "Crane")).to(equal(["Crane.polisher", "Polisher.buff", "WaxPolisher.buff"]))

            with it("should join a call on the object a field that holds a class builds"):
                expect(_invoked(self.fixture, "fresh", "Buffer")).to(equal(["Buffer.pad_type", "Polisher.buff", "WaxPolisher.buff"]))

            with it("should join a call on the object built by calling the class a call answers"):
                expect(_invoked(self.fixture, "made", "Buffer")).to(equal(["Buffer.pad_kind", "Polisher.buff", "WaxPolisher.buff"]))

            with it("should join a call on the object built by calling a local that holds a class"):
                expect(_invoked(self.fixture, "fresh_all", "Buffer")).to(equal(["Polisher.buff", "WaxPolisher.buff"]))

            with it("should join a call on what an operation answers in the type a field's hint passes the generic class"):
                expect(_invoked(self.fixture, "turn_one", "WrenchRack")).to(equal(["Shelving.first", "Wrench.turn", "WrenchRack.rack"]))

            with it("should join a call on each item a property answers in the type a field's hint passes the generic class"):
                expect(_invoked(self.fixture, "turn_stock", "WrenchRack")).to(equal(["Shelving.stock", "Wrench.turn", "WrenchRack.rack"]))

            with it("should join a mixin's super() to the next class that declares it in the order of each class mixing it in"):
                expect(_invoked(self.fixture, "move", "Ordered")).to(equal(["Mover.move"]))

            with it("should read a comprehension's local as what that comprehension walks, not an earlier one of the same name"):
                expect(_invoked(self.fixture, "wiped", "Car")).to(contain("Wiper.record"))

            with it("should join a call a comprehension makes on each item it takes"):
                expect(_invoked(self.fixture, "all_records", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record", "Tyres.record"]))

            with it("should join a call on each item of a list a comprehension builds"):
                expect(_invoked(self.fixture, "kept_records", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record", "Tyres.record"]))
            with it("should join a call on each item of a list of a base class to the operation every class extending the base overrides"):
                expect(_invoked(self.fixture, "inspect_all", "Car")).to(equal(["Brakes.record", "Inspection.record", "Lights.record", "Tyres.record"]))

            with it("should join a call a property's getter makes through the field of the class a factory returns"):
                expect(_invoked(self.fixture, "garage_open", "Car")).to(equal(["Opener.load", "Opener.remote", "Remote.press"]))

            with it("should join a call through a module's name to the function that module declares"):
                expect(_invoked(self.fixture, "buff", "Car")).to(equal(["_module.shine"]))

            with it("should join a function handed over as a value"):
                expect(_invoked(self.fixture, "schedule", "Car")).to(equal(["_module._odometer"]))

            with it("should join an operation and a module's function read without a call and passed on"):
                expect(_invoked(self.fixture, "hooks", "Car")).to(equal(["Car.drive", "_module.wax"]))

            with it("should mark no call joined by its receiver's class"):
                expect(_invoke_facts(self.fixture, "fill", "Pump.pour")).to(equal({}))

            with it("should count on the class each call it could not join whose receiver is an object from outside the code, a built-in one the code assigns with no hint included"):
                expect(_class_named(self.fixture, "Car").get_fact("unresolved_calls_on_outside_objects")).to(equal(4))

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

    with context("with React components"):
        with before.all:
            self.fixture = practice_from_files(_SHELL)

        with it("should join a function that renders components as elements to the class component's render and the function component"):
            expect(_invoked(self.fixture, "Page", "_module")).to(equal(["Boundary.render", "_module.Banner"]))

        with it("should join a call through a field an interface types"):
            expect(_invoked(self.fixture, "change", "Filter")).to(contain("Status.failed"))

        with it("should join a function a script calls after a spread"):
            expect(_invoked(self.fixture, "allMarks", "_module")).to(equal(["_module.changeMarks", "_module.commentMarks"]))

        with it("should join an operation a script calls on its own object after a spread"):
            expect(_invoked(self.fixture, "list", "Marks")).to(equal(["Marks.extra"]))

        with it("should join a function a script reaches through its bind"):
            expect(_invoked(self.fixture, "foldAll", "_module")).to(equal(["_module.foldAt"]))

        with it("should join a function a template string's expression hands to a call"):
            expect(_invoked(self.fixture, "labelOf", "_module")).to(equal(["_module.markShown"]))

        with it("should join a call a script's own statements make, as made by the folder that holds it"):
            expect(_invoked_by_folder(self.fixture, "shell")).to(equal(["_module.boot"]))

        with it("should keep that a class rendering a class component as an element creates it on each call"):
            expect(_reached(self.fixture, "View", "Boundary")).to(equal(["created on each call"]))

    with context("with JavaScript classes"):
        with before.all:
            self.fixture = practice_from_files(_FLEET_JAVASCRIPT)

        with it("should read the part the class builds in its constructor as a composition"):
            expect(_classes_related(self.fixture, "composition", "Van")).to(equal(["Engine"]))

        with it("should keep that the class creates its part in the constructor and calls it through the field"):
            expect(_reached(self.fixture, "Van", "Engine")).to(equal(["created in the constructor", "held as a field"]))
