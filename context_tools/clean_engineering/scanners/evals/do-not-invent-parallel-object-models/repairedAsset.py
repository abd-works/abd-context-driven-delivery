"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
"""
# Repaired: thin wrappers over live objects - no parallel *Model/*Entry scrape.


class CatalogTool:
    def __init__(self, repo_url: str, ref: str):
        self.repo_url = repo_url
        self.ref = ref

    def generate_catalog(self, tool, owner) -> str:
        return str(getattr(tool, "name", tool))


class CatalogAction:
    def __init__(self, repo_url: str, ref: str, catalog_tool: CatalogTool):
        self.catalog_tool = catalog_tool

    def generate_catalog(self, action, owner) -> str:
        return self.catalog_tool.generate_catalog(action, owner)


class Catalog:
    def __init__(self, catalog_action: CatalogAction):
        self.catalog_action = catalog_action

    def generate_catalog(self, owner) -> str:
        return self.catalog_action.generate_catalog(owner.actions["generate"], owner)
