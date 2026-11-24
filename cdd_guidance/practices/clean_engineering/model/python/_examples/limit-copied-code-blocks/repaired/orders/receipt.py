"""The receipt asks the invoice, which works out the cost in one place."""

from billing.invoice import Invoice


class Receipt:
    def __init__(self, invoice: Invoice) -> None:
        self._invoice = invoice

    def amount_due(self, lines: list, discount: int, tax_rate: int, minimum_charge: int) -> int:
        return self._invoice.total(lines, discount, tax_rate, minimum_charge)
