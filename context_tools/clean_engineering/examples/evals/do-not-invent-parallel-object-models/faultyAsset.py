"""Faulty: parallel CatalogModel + *Entry family filled by a scraper."""


class PracticeEntry:
    def __init__(self, name: str, fidelities: list["FidelityEntry"]):
        self.name = name
        self.fidelities = fidelities


class FidelityEntry:
    def __init__(self, name: str, actions: list["LifecycleActionEntry"]):
        self.name = name
        self.actions = actions


class LifecycleActionEntry:
    def __init__(self, name: str, tools: list[str]):
        self.name = name
        self.tools = tools


class UtilityEntry:
    def __init__(self, name: str, tools: list[str]):
        self.name = name
        self.tools = tools


class CatalogModel:
    def __init__(self, practices: list[PracticeEntry], utilities: list[UtilityEntry]):
        self.practices = practices
        self.utilities = utilities


class CatalogScraper:
    def scrape(self, roster) -> CatalogModel:
        practices = [
            PracticeEntry(
                name=toolset.__class__.__name__,
                fidelities=[
                    FidelityEntry(
                        name=fidelity_name,
                        actions=[
                            LifecycleActionEntry(name=action_name, tools=[])
                            for action_name in toolset.actions
                        ],
                    )
                    for fidelity_name in toolset.fidelities
                ],
            )
            for toolset in roster.context_tools
        ]
        utilities = [
            UtilityEntry(name=name, tools=list(utility.tools))
            for name, utility in roster.utilities.items()
        ]
        return CatalogModel(practices=practices, utilities=utilities)
