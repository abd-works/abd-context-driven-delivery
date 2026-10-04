class Client:
    def validate_last_transaction(self, account):
        return account.balance + account.holds - account.pending


class Catalog:
    def __init__(self):
        self.title = ""
        self.items = []


class CatalogCard:
    def from_catalog(self, catalog: Catalog) -> "CatalogCard":
        return CatalogCard()


class Printer:
    def catalog_html(self, catalog: Catalog) -> str:
        rows = "".join(item.name for item in catalog.items)
        return catalog.title + rows


class Shelf:
    def public_terms(self):
        return []


class Layout:
    def shelf_height(self, shelf: Shelf) -> int:
        return self._shelf_header_height(shelf)

    def _shelf_header_height(self, shelf: Shelf) -> int:
        terms = shelf.public_terms()
        if not terms:
            return 24
        return 24 + min(8, len(terms)) * 12
