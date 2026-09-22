class Client:
    def validate_last_transaction(self, account):
        return account.balance + account.holds - account.pending
