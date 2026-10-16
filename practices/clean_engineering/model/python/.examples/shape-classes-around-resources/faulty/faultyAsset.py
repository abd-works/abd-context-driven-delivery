class PaymentData:
    amount: int
    source: str
    destination: str


class PaymentService:
    def move(self, payment_data: PaymentData):
        return payment_data.amount


class Module:
    name: str
    sequential_order: int


class GraphCleanEngineeringModel:
    def load_module(self, source: Module):
        return source.name
