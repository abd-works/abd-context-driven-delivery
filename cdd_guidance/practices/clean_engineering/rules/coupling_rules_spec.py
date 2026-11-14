"""Coupling rules compare a class with every other class in the graph, by shape rather than by name."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    ce_rule_by_slug,
    files_rule_pair,
    practice_from_files,
    rule_pair,
)


def _hits(slug: str, fixture) -> list[str]:
    return fixture.hits(ce_rule_by_slug(slug))


_PAYMENT_DATA = "class PaymentData:\n    amount: int\n    source: str\n    destination: str\n"
_PAYMENT = (
    "class Payment:\n    amount: int\n    source: str\n    destination: str\n\n"
    "    def move(self) -> int:\n        return self.amount\n"
)
_ORDER_RECORD = "class OrderRecord:\n    customer: str\n    total: int\n    placed_at: str\n    lines: list\n"


with description("classes compared across the graph"):
    # Each fixture builds a graph, so every context builds its fixtures once, before its examples, which only run the rules.
    with context("shape-classes-around-resources"):
        with before.all:
            self.pair = files_rule_pair(
                "shape-classes-around-resources",
                {
                    "pay/payment_data.py": _PAYMENT_DATA,
                    "pay/payment_service.py": "class PaymentService:\n    def move(self, payment: PaymentData) -> int:\n        return payment.amount\n",
                },
                {"pay/payment.py": _PAYMENT},
            )
            self.module_and_class = practice_from_files(
                {
                    "model/model.py": (
                        "class Module:\n    name: str\n\n    def load_classes(self) -> list:\n        return []\n\n\n"
                        "class OoadClass:\n    name: str\n\n    def operations(self) -> list:\n        return []\n"
                    )
                }
            )

        with it("should flag a stateless service whose operation takes a data bag from another file"):
            self.pair.check()

        with it("should accept classes named Module and OoadClass that hold state and behavior"):
            expect(_hits("shape-classes-around-resources", self.module_and_class)).to(equal([]))

    with context("do-not-invent-parallel-object-models"):
        with before.all:
            self.copied_fields = files_rule_pair(
                "do-not-invent-parallel-object-models",
                {
                    "orders/order.py": "class Order:\n    customer: str\n    total: int\n    placed_at: str\n\n    def cancel(self) -> None:\n        return None\n",
                    "reports/order_record.py": _ORDER_RECORD,
                },
                {
                    "orders/order.py": "class Order:\n    customer: str\n    total: int\n    placed_at: str\n\n    def cancel(self) -> None:\n        return None\n",
                    "reports/order_report.py": "class OrderReport:\n    order: Order\n    printed_at: str\n",
                },
            )
            self.name_copy = files_rule_pair(
                "do-not-invent-parallel-object-models",
                {
                    "board/column.py": "class Column:\n    title: str\n",
                    "board/ticket.py": "class Ticket:\n    def __init__(self, column_name: str) -> None:\n        self.column_name = column_name\n",
                },
                {
                    "board/column.py": "class Column:\n    title: str\n",
                    "board/ticket.py": "class Ticket:\n    def __init__(self, column: Column) -> None:\n        self.column = column\n",
                },
            )
            self.failure_name = practice_from_files(
                {
                    "tools/action.py": "class Action:\n    name: str\n",
                    "tools/errors.py": (
                        "class ToolError(Exception):\n    pass\n\n\n"
                        "class AgentToolValidationError(ToolError):\n    def __init__(self, action_name: str) -> None:\n"
                        "        self.action_name = action_name\n"
                    ),
                }
            )
            self.dict_per_member = files_rule_pair(
                "do-not-invent-parallel-object-models",
                {
                    "practice/fidelity.py": "class Fidelity:\n    state: str\n",
                    "practice/session.py": "class Session:\n    fidelity_states: dict[str, str]\n",
                },
                {
                    "practice/fidelity.py": "class Fidelity:\n    state: str\n",
                    "practice/session.py": "class Session:\n    fidelities: dict[str, Fidelity]\n",
                },
            )
            self.named_class = files_rule_pair(
                "do-not-invent-parallel-object-models",
                {
                    "tools/action.py": "class Action:\n    name: str\n",
                    "tools/invoke.py": "class Invoke:\n    def __init__(self, action_name: str) -> None:\n        self._action_name = action_name\n",
                },
                {
                    "tools/mcp.py": "class Mcp:\n    flag = '_mcp'\n",
                    "tools/tool.py": "class Tool:\n    def __init__(self, mcp_name: str) -> None:\n        self.mcp_name = mcp_name\n",
                },
            )
            self.three_fields = files_rule_pair(
                "do-not-invent-parallel-object-models",
                {
                    "agent/run.py": "class RunResponse:\n    instructions: str\n    tools: list\n    result: str\n\n    def ok(self) -> bool:\n        return True\n",
                    "agent/expansion.py": "class ExpansionResult:\n    instructions: str\n    tools: list\n    result: str\n",
                },
                {
                    "agent/run.py": "class RunResponse:\n    instructions: str\n    tools: list\n    result: str\n\n    def ok(self) -> bool:\n        return True\n",
                    "agent/expansion.py": "class ExpansionResult:\n    instructions: list\n    tools: dict\n    result: int\n",
                },
            )
            self.mixin = practice_from_files(
                {
                    "model/parse.py": "class BraceParse:\n    language: str\n    operation_type: type\n    property_type: type\n\n    def parse(self) -> int:\n        return 1\n",
                    "model/code.py": (
                        "class CodeClass:\n    language: str\n    operation_type: type = int\n    property_type: type = str\n\n\n"
                        "class CodeModel:\n    pass\n\n\nclass BraceModel(BraceParse, CodeModel):\n    pass\n"
                    ),
                }
            )
            self.member_values = files_rule_pair(
                "do-not-invent-parallel-object-models",
                {
                    "story/source.py": "class Source:\n    text: str\n",
                    "story/model.py": "class StoryModel:\n    source_texts: dict[str, str]\n",
                },
                {
                    "story/source.py": "class Source:\n    file: str\n",
                    "story/model.py": "class StoryModel:\n    source_texts: dict[str, str]\n",
                },
            )
            self.type_objects = practice_from_files(
                {
                    "graph/edge.py": "class Edge:\n    kind: str\n\n\nclass EdgeType:\n    order: int\n",
                    "graph/nodes.py": "class PracticeNodes:\n    _edge_types: dict[str, EdgeType]\n",
                }
            )
            self.number_keys = practice_from_files(
                {
                    "recipe/loop.py": "class Loop:\n    item: str\n",
                    "recipe/expansion.py": "class RecipeExpansion:\n    _loop_item_modes: dict[int, str]\n",
                }
            )
            self.one_owner = practice_from_files(
                {
                    "kanban/board.py": (
                        "class Board:\n    columns: list\n\n\nclass Card:\n    _board: Board\n\n    def move(self) -> int:\n        return 1\n\n\n"
                        "class BoardReads:\n    _board: Board\n\n    def cards(self) -> int:\n        return 1\n"
                    ),
                }
            )
            self.named_owner = practice_from_files(
                {
                    "orders/order.py": "class Order:\n    customer: str\n    total: int\n    placed_at: str\n    lines: list\n    status: str\n",
                    "reports/order_record.py": _ORDER_RECORD,
                }
            )

        with it("should flag a class in another file that copies most of an owner's fields"):
            self.copied_fields.check()

        with it("should flag a name copy of a reference to another class"):
            self.name_copy.check()

        with it("should accept a failure that keeps the name of what it failed on, for its message"):
            expect(_hits("do-not-invent-parallel-object-models", self.failure_name)).to(equal([]))

        with it("should flag a dict holding one value per member, keyed by the member's name"):
            self.dict_per_member.check()

        with it("should flag a name copy of a class that has a name and accept one of a class that has none"):
            self.named_class.check()

        with it("should flag classes sharing three fields of one type each and accept three names of different types"):
            self.three_fields.check()

        with it("should accept a mixin's annotations, which declare what the class it is mixed into holds"):
            expect(_hits("do-not-invent-parallel-object-models", self.mixin)).to(equal([]))

        with it("should flag a dict of one value per member the member holds, and accept one of values it does not"):
            self.member_values.check()

        with it("should accept a dict of each kind's own type object, named after the member class"):
            expect(_hits("do-not-invent-parallel-object-models", self.type_objects)).to(equal([]))

        with it("should accept a dict keyed by a number, whose values are names"):
            expect(_hits("do-not-invent-parallel-object-models", self.number_keys)).to(equal([]))

        with it("should accept two classes of one file that each hold the one object they belong to"):
            expect(_hits("do-not-invent-parallel-object-models", self.one_owner)).to(equal([]))

        with it("should name the copied fields and the owner"):
            expect(_hits("do-not-invent-parallel-object-models", self.named_owner)).to(
                contain("Class 'OrderRecord' copies the fields ['customer', 'lines', 'placed_at', 'total'] of 'Order'. Use one canonical model type.")
            )

    with context("layer-separation"):
        with before.all:
            self.pair = rule_pair(
                "layer-separation",
                "class Cart:\n    def subtotal(self) -> int:\n        return 0\n\n\nclass CartView:\n    def subtotal(self, cart: Cart) -> int:\n        return cart.subtotal()\n",
                "class Cart:\n    def subtotal(self) -> int:\n        return 0\n\n\nclass CartView:\n    def subtotal(self, cart: Cart) -> str:\n        total = cart.subtotal()\n        return f'{total:.2f}'\n",
            )
            self.forwarding_module = practice_from_files(
                {
                    "shop/cart/cart.py": "class Cart:\n    def subtotal(self) -> int:\n        return 0\n\n    def checkout(self) -> int:\n        return 1\n",
                    "shop/api/cart_api.py": "class CartApi:\n    def subtotal(self, cart: Cart) -> int:\n        return cart.subtotal()\n\n    def checkout(self, cart: Cart) -> int:\n        return cart.checkout()\n",
                }
            )

        with it("should flag a class whose only operation forwards to another class, whatever its name"):
            self.pair.check()

        with it("should flag a module folder whose classes only forward to one other module"):
            expect(_hits("layer-separation", self.forwarding_module)).to(contain("Module 'api' only forwards to 'cart'; collapse the pass-through module."))
