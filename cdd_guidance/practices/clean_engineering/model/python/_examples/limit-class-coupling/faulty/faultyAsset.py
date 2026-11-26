"""The dashboard counts every source itself, so it depends on fifteen classes: a change to any of them can break it."""


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


class Dashboard:
    def summary(self) -> dict[str, int]:
        return {
            "orders": Orders().count(),
            "refunds": Refunds().count(),
            "payments": Payments().count(),
            "invoices": Invoices().count(),
            "coupons": Coupons().count(),
            "stock": Stock().count(),
            "suppliers": Suppliers().count(),
            "shipments": Shipments().count(),
            "returns": Returns().count(),
            "warehouses": Warehouses().count(),
            "customers": Customers().count(),
            "reviews": Reviews().count(),
            "subscriptions": Subscriptions().count(),
            "complaints": Complaints().count(),
            "referrals": Referrals().count(),
        }
