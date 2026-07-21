"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
class Cart:
    def __init__(self, owner):
        self._owner = owner

    @property
    def owner(self):
        return self._owner
