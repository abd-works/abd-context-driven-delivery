"""Coupling rules compare a class with every other class in the graph, by shape rather than by name."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    assert_files_rule_pair,
    assert_rule_pair,
    ce_rule_by_slug,
    practice_from_files,
)


def _hits(slug: str, files: dict[str, str]) -> list[str]:
    return practice_from_files(files).hits(ce_rule_by_slug(slug))


_PAYMENT_DATA = "class PaymentData:\n    amount: int\n    source: str\n    destination: str\n"
_PAYMENT = (
    "class Payment:\n    amount: int\n    source: str\n    destination: str\n\n"
    "    def move(self) -> int:\n        return self.amount\n"
)
_ORDER_RECORD = "class OrderRecord:\n    customer: str\n    total: int\n    placed_at: str\n    lines: list\n"


with description("classes compared across the graph"):
    with context("shape-classes-around-resources"):
        with it("should flag a stateless service whose operation takes a data bag from another file"):
            assert_files_rule_pair(
                "shape-classes-around-resources",
                {
                    "pay/payment_data.py": _PAYMENT_DATA,
                    "pay/payment_service.py": "class PaymentService:\n    def move(self, payment: PaymentData) -> int:\n        return payment.amount\n",
                },
                {"pay/payment.py": _PAYMENT},
            )

        with it("should accept classes named Module and OoadClass that hold state and behavior"):
            source = (
                "class Module:\n    name: str\n\n    def load_classes(self) -> list:\n        return []\n\n\n"
                "class OoadClass:\n    name: str\n\n    def operations(self) -> list:\n        return []\n"
            )
            expect(_hits("shape-classes-around-resources", {"model/model.py": source})).to(equal([]))

    with context("do-not-invent-parallel-object-models"):
        with it("should flag a class in another file that copies most of an owner's fields"):
            assert_files_rule_pair(
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

        with it("should flag a name copy of a reference to another class"):
            assert_files_rule_pair(
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

        with it("should accept a failure that keeps the name of what it failed on, for its message"):
            files = {
                "tools/action.py": "class Action:\n    name: str\n",
                "tools/errors.py": (
                    "class ToolError(Exception):\n    pass\n\n\n"
                    "class AgentToolValidationError(ToolError):\n    def __init__(self, action_name: str) -> None:\n"
                    "        self.action_name = action_name\n"
                ),
            }
            expect(_hits("do-not-invent-parallel-object-models", files)).to(equal([]))

        with it("should flag a dict holding one value per member, keyed by the member's name"):
            assert_files_rule_pair(
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

        with it("should name the copied fields and the owner"):
            hits = _hits(
                "do-not-invent-parallel-object-models",
                {
                    "orders/order.py": "class Order:\n    customer: str\n    total: int\n    placed_at: str\n    lines: list\n    status: str\n",
                    "reports/order_record.py": _ORDER_RECORD,
                },
            )
            expect(hits).to(contain("Class 'OrderRecord' copies the fields ['customer', 'lines', 'placed_at', 'total'] of 'Order'. Use one canonical model type."))

    with context("layer-separation"):
        with it("should flag a class whose only operation forwards to another class, whatever its name"):
            assert_rule_pair(
                "layer-separation",
                "class Cart:\n    def subtotal(self) -> int:\n        return 0\n\n\nclass CartView:\n    def subtotal(self, cart: Cart) -> int:\n        return cart.subtotal()\n",
                "class Cart:\n    def subtotal(self) -> int:\n        return 0\n\n\nclass CartView:\n    def subtotal(self, cart: Cart) -> str:\n        total = cart.subtotal()\n        return f'{total:.2f}'\n",
            )

        with it("should flag a module folder whose classes only forward to one other module"):
            hits = _hits(
                "layer-separation",
                {
                    "shop/cart/cart.py": "class Cart:\n    def subtotal(self) -> int:\n        return 0\n\n    def checkout(self) -> int:\n        return 1\n",
                    "shop/api/cart_api.py": "class CartApi:\n    def subtotal(self, cart: Cart) -> int:\n        return cart.subtotal()\n\n    def checkout(self, cart: Cart) -> int:\n        return cart.checkout()\n",
                },
            )
            expect(hits).to(contain("Module 'api' only forwards to 'cart'; collapse the pass-through module."))
