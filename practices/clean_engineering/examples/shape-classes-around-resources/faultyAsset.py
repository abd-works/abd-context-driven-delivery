class PaymentData:
    amount: int
    source: str
    destination: str


class PaymentService:
    def move(self, payment_data: PaymentData):
        return payment_data.amount
