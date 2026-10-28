class CustomerRepository:
    def __init__(self, session):
        self._session = session
        self._customers = {}

    def load(self):
        return self._customers.get(self._session.customer_id)
