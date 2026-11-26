"""Each panel counts the sources of one area, and the dashboard asks the three panels: no class depends on more
than five others."""


class Orders:
    def count(self) -> int:
        return 0


class Refunds:
    def count(self) -> int:
        return 0


class Payments:
    def count(self) -> int:
        return 0


class Invoices:
    def count(self) -> int:
        return 0


class Coupons:
    def count(self) -> int:
        return 0


class Stock:
    def count(self) -> int:
        return 0


class Suppliers:
    def count(self) -> int:
        return 0


class Shipments:
    def count(self) -> int:
        return 0


class Returns:
    def count(self) -> int:
        return 0


class Warehouses:
    def count(self) -> int:
        return 0


class Customers:
    def count(self) -> int:
        return 0


class Reviews:
    def count(self) -> int:
        return 0


class Subscriptions:
    def count(self) -> int:
        return 0


class Complaints:
    def count(self) -> int:
        return 0


class Referrals:
    def count(self) -> int:
        return 0


class SalesPanel:
    def summary(self) -> dict[str, int]:
        return {
            "orders": Orders().count(),
            "refunds": Refunds().count(),
            "payments": Payments().count(),
            "invoices": Invoices().count(),
            "coupons": Coupons().count(),
        }


class StockPanel:
    def summary(self) -> dict[str, int]:
        return {
            "stock": Stock().count(),
            "suppliers": Suppliers().count(),
            "shipments": Shipments().count(),
            "returns": Returns().count(),
            "warehouses": Warehouses().count(),
        }


class CustomersPanel:
    def summary(self) -> dict[str, int]:
        return {
            "customers": Customers().count(),
            "reviews": Reviews().count(),
            "subscriptions": Subscriptions().count(),
            "complaints": Complaints().count(),
            "referrals": Referrals().count(),
        }


class Dashboard:
    def summary(self) -> dict[str, int]:
        return {**SalesPanel().summary(), **StockPanel().summary(), **CustomersPanel().summary()}
