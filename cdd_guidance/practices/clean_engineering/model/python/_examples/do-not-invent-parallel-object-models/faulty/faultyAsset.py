class Practice:
    name: str
    folder: str
    fidelities: list

    def first_fidelity(self) -> str:
        return self.fidelities[0]


class PracticeEntry:
    name: str
    folder: str
    fidelities: list


class CatalogScraper:
    def scrape(self, practice: Practice) -> PracticeEntry:
        entry = PracticeEntry()
        entry.name = practice.name
        return entry
