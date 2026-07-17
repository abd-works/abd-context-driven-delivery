"""
# @toolset-manifest python -m tools manifest clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: clean_engineering.clean_engineering:CleanEngineering

CleanEngineering Python template — one class family per file (`cohesive-file`).

A file holds the primary type, its subtypes, and tightly connected peers
(e.g. Ability + Abilities in abilities.py). Not one class per file.

Layout (`physical-folder`): write each file under the **module** folder
(e.g. `{module_slug}/{family_slug}.py`), not outside it. Module context:
`{module_slug}/.context/module-context.md`. A chapter/organisational parent
may hold several modules; do not collapse a chapter into one module.

Naming (mirrors the compact markdown template):
    File            {family_slug}.py        (snake_case family concept, e.g. abilities.py)
    Class           PascalCase              (matches the class name)
    Property        snake_case              (real terms)
    Operation       snake_case              (verb-noun)
    Invariant       comment at M/S          (plain-English sentence)
    Invariant       abstract method at E    (name IS the rule; docstring IS the sentence)
    Interaction     abstract method at S+   (name IS the summary)

Member docs: docstring sits **above** the property or operation it describes
(not below, not as a trailing `#` comment).

Doc-comment tag dictionary (specification fidelity only):
    @composition / @aggregation / @association   on property (in its docstring)
    @invariant                                   on abstract method (E only)
    @interaction                                 on abstract method
"""

from __future__ import annotations
from abc import ABC, abstractmethod

# Fidelity tags — each element is annotated with the fidelity that introduced it.
# To generate at a given fidelity, include all elements tagged at or below it:
#   L  = language      (class + docstring only)
#   M  = model         (typed properties, operation stubs, relationships named)
#   S  = specification (relationship kinds, invariant comments, interactions)
#   E  = engineering   (full implementations; invariants become abstract methods)


class ClassName(ABC):                                                   # L
    """{*ClassName* is — one sentence: what it is, its unique role.
    Identity only. No relationship or behavior sentences here.}"""     # L

    # -- Properties -----------------------------------------------------------

    """{sentence about this property — what it holds and why.}         # L
    @composition"""                                                     # S
    owned_property: Type                                                # M

    """{sentence about this collection — what it gathers.}             # L
    @aggregation"""                                                     # S
    collected_property: list[Type]                                      # M

    """{sentence about this relationship — what it depends on.}        # L
    @association"""                                                     # S
    referenced_property: Type                                           # M

    """{sentence about this plain property.}"""                         # L
    plain_property: Type                                                # M
    # Invariant: {constraint sentence — the rule in plain English.}    # M

    # -- Constructor ----------------------------------------------------------

    @abstractmethod
    def __init__(self, param: Type) -> None: ...                        # M

    def __init__(self, param: Type) -> None:                            # E
        self._plain_property = param                                    # E

    # -- Public operations ----------------------------------------------------

    """{language bullet for this operation}"""                          # L
    # Invariant: {constraint sentence applicable to this operation.}   # S
    @abstractmethod
    def operation_name(self, param: Type) -> ReturnType: ...            # M

    def operation_name(self, param: Type) -> ReturnType:                # E
        """{language bullet for this operation}"""                      # L
        ...                                                             # E

    """{language bullet for this operation}"""                          # L
    @abstractmethod
    def another_operation(self) -> ReturnType: ...                      # M

    def another_operation(self) -> ReturnType:                          # E
        """{language bullet for this operation}"""                      # L
        ...                                                             # E

    # -- Private operations ---------------------------------------------------

    """{what this helper does}"""                                       # S
    @abstractmethod
    def _private_helper(self, param: Type) -> ReturnType: ...           # S

    def _private_helper(self, param: Type) -> ReturnType:               # E
        """{what this helper does}"""                                   # S
        ...                                                             # E

    # -- Invariants -----------------------------------------------------------

    @abstractmethod
    def rule_stated_as_a_method_name(self) -> None:                     # E
        """@invariant — {constraint sentence repeated as docstring.}"""
        ...

    # -- Interactions ---------------------------------------------------------

    @abstractmethod
    def interaction_summary_as_a_method_name(self) -> None:             # S
        """@interaction"""
        ...


# Subtype — delta only; parent members are inherited, not repeated     # M
class ChildClass(ClassName):                                            # M
    """{delta — what ChildClass adds or overrides, not what it inherits}"""  # L

    """{delta property sentence}"""                                     # L
    delta_property: Type                                                # M

    """{delta operation sentence}"""                                    # L
    @abstractmethod
    def delta_operation(self, param: Type) -> ReturnType: ...           # M

    def delta_operation(self, param: Type) -> ReturnType:               # E
        """{delta operation sentence}"""                                # L
        ...                                                             # E
