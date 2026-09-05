"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to context_tools/language-tools.md for tool recommendations.
# =============================================================================
# A production file holds the public seam (I{Class} when one exists), the 
# production Class, subtypes, and tightly connected peers. 
# Example factories are ALWAYS in a separate sibling file.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
class {ClassName}:
    """*{ClassName}* unique role."""
    
    @property
    def {property}(self) -> {Type}:
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...
