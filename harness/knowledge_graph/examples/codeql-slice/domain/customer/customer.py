"""Slice production types for CodeQL extract."""


class Identity:
    def __init__(self, id: str) -> None:
        self.id = id


class Customer:
    def __init__(self, identity: Identity) -> None:
        self.identity = identity


class IMavenirClient:
    def fetch_customer(self, customer_id: str) -> Customer:
        return Customer(Identity(customer_id))


class CustomerRepository:
    def __init__(self, client: IMavenirClient) -> None:
        self._client = client

    def load(self, customer_id: str) -> Customer:
        return self._client.fetch_customer(customer_id)

    def create(self) -> Customer:
        return Customer(Identity(""))
