class Account:
    def __init__(self) -> None:
        self._balance = 0
        self._holds = 0

    def covers_holds(self) -> bool:
        return self._balance - self._holds >= 0


class Client:
    def validate_last_transaction(self, account: Account) -> bool:
        return account.covers_holds()
