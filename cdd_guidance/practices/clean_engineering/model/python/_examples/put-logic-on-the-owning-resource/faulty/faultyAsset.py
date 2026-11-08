class Account:
    def __init__(self) -> None:
        self._balance = 0
        self._holds = 0


class Client:
    def validate_last_transaction(self, account: Account) -> bool:
        return account._balance - account._holds >= 0
