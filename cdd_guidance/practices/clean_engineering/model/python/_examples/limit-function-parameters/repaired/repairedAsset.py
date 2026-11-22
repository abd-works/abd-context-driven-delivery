class Parcel:
    """A parcel on its way to a customer."""

    def __init__(self, address: "Address") -> None:
        self._address = address

    def send(self, carrier: str, insured: bool) -> str:
        return f"{self._address} {carrier} {insured}"
