from money.money import RefundPolicy


class Refund:
    def __init__(self, held: RefundPolicy) -> None:
        self._held = held

    def policy(self) -> RefundPolicy:
        return self._held
