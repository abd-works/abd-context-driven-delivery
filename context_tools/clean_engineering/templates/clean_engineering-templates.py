"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to context_tools/language-tools.md for tool recommendations.
# =============================================================================
# Put a class family in one file: the primary type, its subtypes, and
# tightly connected peers that only make sense together (element +
# collection, small aggregate + its part). Name the file after the family
# concept (`abilities.py` for Ability + Abilities). Split into another
# file only when a type is independently reused across families or the
# file becomes a grab-bag. Do not default to one class per file.
# Default: Class is the seam. I{ClassName} is not the default — add it in
# this same file when multiple implementations sit behind one seam, or when
# the user asks. Public members only on I{ClassName}; private members stay
# on {ClassName}. Put `{Type}ExampleFactory` in a sibling file — never in
# the production family file. Write each file under the module folder
# (`{module}/{family_slug}.py`), not beside the module.
# Invariants, interactions, comments (model):
#   Write each invariant as `#` on the class (or above the property /
#   operation it constrains): a must / never / always / before / after
#   that stays true when the object acts.
#   Write each interaction as `-> {collaborator}.{operation}` nested
#   under the calling operation. `-> ClassName` alone is not an interaction.
#   State an invariant or a sequence with `#`. Leave every other line
#   uncommented.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
# Optional — omit unless generating an interface:
class I{ClassName}(ABC):
    @property
    @abstractmethod
    def {property}(self) -> {Type}:
        ...

    @abstractmethod
    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

class {ClassName}:  # or class {ClassName}(I{ClassName}):
    """*{ClassName}* unique role."""
    # {must / never / always / before / after that stays true of the object}

    @property
    def {property}(self) -> {Type}:
        # {must / never / always / before / after about this property}
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        # {must / never / always / before / after when this operation runs}
        # -> {collaborator}.{operation}
        ...

    def _{private_helper}(self, {param}: {Type}) -> {Type}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...
