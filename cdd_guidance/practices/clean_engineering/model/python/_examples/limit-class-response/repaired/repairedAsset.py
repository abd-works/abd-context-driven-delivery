"""Each part adds up its own amounts, and the invoice asks each part for its subtotal: one call to total sets off
three methods of other classes."""


class Charges:
    def delivery(self) -> int:
        return 0

    def packing(self) -> int:
        return 0

    def insurance(self) -> int:
        return 0

    def handling(self) -> int:
        return 0

    def gift_wrap(self) -> int:
        return 0

    def express(self) -> int:
        return 0

    def weekend(self) -> int:
        return 0

    def remote_area(self) -> int:
        return 0

    def fragile(self) -> int:
        return 0

    def oversize(self) -> int:
        return 0

    def storage(self) -> int:
        return 0

    def customs(self) -> int:
        return 0

    def fuel(self) -> int:
        return 0

    def pallet(self) -> int:
        return 0

    def signature(self) -> int:
        return 0

    def collection(self) -> int:
        return 0

    def returns_label(self) -> int:
        return 0

    def subtotal(self) -> int:
        return self.delivery() + self.packing() + self.insurance() + self.handling() + self.gift_wrap() + self.express() + self.weekend() + self.remote_area() + self.fragile() + self.oversize() + self.storage() + self.customs() + self.fuel() + self.pallet() + self.signature() + self.collection() + self.returns_label()


class Fees:
    def card(self) -> int:
        return 0

    def currency(self) -> int:
        return 0

    def late(self) -> int:
        return 0

    def admin(self) -> int:
        return 0

    def paper_bill(self) -> int:
        return 0

    def reminder(self) -> int:
        return 0

    def setup(self) -> int:
        return 0

    def cancellation(self) -> int:
        return 0

    def rebooking(self) -> int:
        return 0

    def change(self) -> int:
        return 0

    def booking(self) -> int:
        return 0

    def service(self) -> int:
        return 0

    def platform(self) -> int:
        return 0

    def listing(self) -> int:
        return 0

    def dispute(self) -> int:
        return 0

    def chargeback(self) -> int:
        return 0

    def refund(self) -> int:
        return 0

    def subtotal(self) -> int:
        return self.card() + self.currency() + self.late() + self.admin() + self.paper_bill() + self.reminder() + self.setup() + self.cancellation() + self.rebooking() + self.change() + self.booking() + self.service() + self.platform() + self.listing() + self.dispute() + self.chargeback() + self.refund()


class Credits:
    def loyalty(self) -> int:
        return 0

    def voucher(self) -> int:
        return 0

    def referral(self) -> int:
        return 0

    def apology(self) -> int:
        return 0

    def price_match(self) -> int:
        return 0

    def bundle(self) -> int:
        return 0

    def student(self) -> int:
        return 0

    def staff(self) -> int:
        return 0

    def senior(self) -> int:
        return 0

    def early_bird(self) -> int:
        return 0

    def bulk(self) -> int:
        return 0

    def seasonal(self) -> int:
        return 0

    def birthday(self) -> int:
        return 0

    def newsletter(self) -> int:
        return 0

    def trade_in(self) -> int:
        return 0

    def survey(self) -> int:
        return 0

    def anniversary(self) -> int:
        return 0

    def subtotal(self) -> int:
        return self.loyalty() + self.voucher() + self.referral() + self.apology() + self.price_match() + self.bundle() + self.student() + self.staff() + self.senior() + self.early_bird() + self.bulk() + self.seasonal() + self.birthday() + self.newsletter() + self.trade_in() + self.survey() + self.anniversary()


class Invoice:
    def __init__(self, charges: Charges, fees: Fees, credits: Credits) -> None:
        self._charges = charges
        self._fees = fees
        self._credits = credits

    def total(self) -> int:
        return self._charges.subtotal() + self._fees.subtotal() - self._credits.subtotal()
