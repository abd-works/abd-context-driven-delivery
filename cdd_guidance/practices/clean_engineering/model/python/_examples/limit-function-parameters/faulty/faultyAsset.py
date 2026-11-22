class Parcel:
    """A parcel on its way to a customer."""

    def send(self, street: str, town: str, postcode: str, country: str, carrier: str, insured: bool) -> str:
        return f"{street} {town} {postcode} {country} {carrier} {insured}"
