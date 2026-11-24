class RefundPolicy:
    def allows(self, days_since_sale: int) -> bool:
        return days_since_sale <= 30


class Refund:
    def __init__(self, held: RefundPolicy) -> None:
        self._held = held

    def policy(self) -> RefundPolicy:
        return self._held
