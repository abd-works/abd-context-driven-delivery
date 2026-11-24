"""The invoice adds up every charge, fee and credit itself: one call to total sets off fifty-one methods of other
classes, and a new charge means changing the invoice."""


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


class Invoice:
    def __init__(self, charges: Charges, fees: Fees, credits: Credits) -> None:
        self._charges = charges
        self._fees = fees
        self._credits = credits

    def total(self) -> int:
        return (
            + self._charges.delivery()
            + self._charges.packing()
            + self._charges.insurance()
            + self._charges.handling()
            + self._charges.gift_wrap()
            + self._charges.express()
            + self._charges.weekend()
            + self._charges.remote_area()
            + self._charges.fragile()
            + self._charges.oversize()
            + self._charges.storage()
            + self._charges.customs()
            + self._charges.fuel()
            + self._charges.pallet()
            + self._charges.signature()
            + self._charges.collection()
            + self._charges.returns_label()
            + self._fees.card()
            + self._fees.currency()
            + self._fees.late()
            + self._fees.admin()
            + self._fees.paper_bill()
            + self._fees.reminder()
            + self._fees.setup()
            + self._fees.cancellation()
            + self._fees.rebooking()
            + self._fees.change()
            + self._fees.booking()
            + self._fees.service()
            + self._fees.platform()
            + self._fees.listing()
            + self._fees.dispute()
            + self._fees.chargeback()
            + self._fees.refund()
            + self._credits.loyalty()
            + self._credits.voucher()
            + self._credits.referral()
            + self._credits.apology()
            + self._credits.price_match()
            + self._credits.bundle()
            + self._credits.student()
            + self._credits.staff()
            + self._credits.senior()
            + self._credits.early_bird()
            + self._credits.bulk()
            + self._credits.seasonal()
            + self._credits.birthday()
            + self._credits.newsletter()
            + self._credits.trade_in()
            + self._credits.survey()
            + self._credits.anniversary()
        )
