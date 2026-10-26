class PracticeEntry:
    name: str


class UtilityEntry:
    name: str


class CatalogScraper:
    def scrape(self, practices: PracticeEntry, utilities: UtilityEntry):
        return practices, utilities
