"""
"""
class Cart:
    def __init__(self, owner):
        self._owner = owner

    @property
    def owner(self):
        return self._owner
