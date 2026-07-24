"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: contexts.clean_engineering.clean_engineering:CleanEngineering

CleanEngineering Python template — two files when Stories-bound:

    {family_slug}.py                 — I{Class} + {Class} (+ subtypes)   PRODUCTION
    {type_slug}_example_factory.py   — I{Class}ExampleFactory + factory  SEPARATE

A production file holds the public seam I{Class}, the production Class that
extends it, subtypes, and tightly connected peers. Not one class per file.
Example factories are NEVER in that file (example-factory-separate-file).

Layout (physical-folder): write each file under the **module** folder
(e.g. {module_slug}/{family_slug}.py). Module context:
{module_slug}/.context/module-context.md.

Naming:
    File (production)  {family_slug}.py
    File (factory)     {type_slug}_example_factory.py
    Interface          I{Class}                (public seam; model fidelity)
    Class              {Class}(I{Class})       (production; specification+)
    ExampleFactory     {Class}ExampleFactory   (plain class; no Loader base; Md+/S+)
    Modes              Fake | Isolated | Production  (factory behavior — not subclasses)
    Property           {owned_property}, …     (snake_case slots)
    Operation          {operation_name}, …     (snake_case slots)
    Params             {param}, {dep}
    Type slots         {Type}, {ReturnType}
    Invariant          comment                 (plain-English; not a method)
    Interaction        abstract method at S    (on Class only; dropped at code)

Fidelity tags:
    L  = language companion (prose; refined every stage — not a fidelity)
    Mu = modules       (thin terms, one-way deps, build order — markdown / module-context)
    Md = model         (I{Class} only — empty public props/ops; optional I{Class}ExampleFactory in factory file)
    S  = specification (Class extends I{Class}; public filled; privates empty on Class;
                       {Class}ExampleFactory modes in sibling factory file when Stories-bound)
    C  = code          (fill remaining empties on Class; drop interactions)
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# =============================================================================
# FILE: {family_slug}.py — production family only (cohesive-file)
# =============================================================================


class I{ClassName}(ABC):                                                # Md
    """*{ClassName}* is — one sentence: what it is, its unique role.
    Identity only. No relationship or behavior sentences here."""     # L

    # -- Public properties (empty interfaces) --------------------------------

    @property                                                           # Md
    @abstractmethod                                                     # Md
    def {owned_property}(self) -> {Type}: ...                           # Md

    @property                                                           # Md
    @abstractmethod                                                     # Md
    def {plain_property}(self) -> {Type}: ...                           # Md

    # -- Public operations (empty interfaces) --------------------------------

    @abstractmethod                                                     # Md
    def __init__(self, {param}: {Type}) -> None: ...                    # Md

    @abstractmethod                                                     # Md
    def {operation_name}(self, {param}: {Type}) -> {ReturnType}: ...    # Md

    @abstractmethod                                                     # Md
    def {another_operation}(self) -> {ReturnType}: ...                  # Md


class {ClassName}(I{ClassName}):                                        # S
    """*{ClassName}* is — one sentence: what it is, its unique role."""  # L

    # -- Public properties (filled at specification) -------------------------

    """{sentence about this property — what it holds and why.}
    @composition"""                                                     # S
    @property                                                           # S
    def {owned_property}(self) -> {Type}:                               # S
        ...                                                             # S

    """{sentence about this plain property.}"""                         # L
    # Invariant: {constraint sentence — the rule in plain English.}    # S
    @property                                                           # S
    def {plain_property}(self) -> {Type}:                               # S
        ...                                                             # S

    # -- Constructor / public operations (filled at specification) -----------

    def __init__(self, {param}: {Type}) -> None:                        # S
        self._{plain_property} = {param}                                # S

    """{language bullet for this operation}"""                          # L
    # Invariant: {constraint sentence applicable to this operation.}   # S
    def {operation_name}(self, {param}: {Type}) -> {ReturnType}:        # S
        ...                                                             # S / C

    def {another_operation}(self) -> {ReturnType}:                      # S
        """{language bullet for this operation}"""                      # L
        ...                                                             # S / C

    # -- Private operations (empty interfaces at S; filled at C) -------------

    """{what this helper does}"""                                       # S
    @abstractmethod                                                     # S
    def _{private_helper}(self, {param}: {Type}) -> {ReturnType}: ...   # S

    def _{private_helper}(self, {param}: {Type}) -> {ReturnType}:       # C
        """{what this helper does}"""                                   # S
        ...                                                             # C

    # -- Interactions (specification only; omit at code) ---------------------

    @abstractmethod                                                     # S
    def {interaction_summary_as_a_method_name}(self) -> None:           # S
        """@interaction"""
        ...


# Subtype — delta only; parent members are inherited, not repeated     # Md/S
class I{ChildClass}(ABC):                                               # Md
    """{delta — what {ChildClass} adds}"""                              # L

    @abstractmethod                                                     # Md
    def {delta_operation}(self, {param}: {Type}) -> {ReturnType}: ...   # Md


class {ChildClass}({ClassName}, I{ChildClass}):                         # S
    """{delta — what {ChildClass} adds or overrides}"""                 # L

    def {delta_operation}(self, {param}: {Type}) -> {ReturnType}:       # S/C
        ...                                                             # S/C


# =============================================================================
# FILE: {type_slug}_example_factory.py — Stories factory (separate file)
# from .{family_slug} import {ClassName}, I{ClassName}
# Pattern only — no ExampleLoader base. examples[{example_key}] is a
# multi-type bundle (not examples[{Type}][…]).
# Fake / Isolated / Production are modes — not Fake{ClassName} subclasses.
# =============================================================================


class I{ClassName}ExampleFactory(ABC):                                  # Md
    """Loads examples[{example_key}] as Fake | Isolated | Production modes."""  # L

    @abstractmethod                                                     # Md
    def load_{example_key}(self, *, mode: str = "fake") -> I{ClassName}: ...  # Md


class {ClassName}ExampleFactory(I{ClassName}ExampleFactory):            # S
    """Fake: mock framework + examples; Isolated: {ClassName}(injected mocks);
    Production: {ClassName}(real collaborators)."""                     # L

    def load_{example_key}(self, *, mode: str = "fake") -> I{ClassName}:  # S
        # examples[{example_key}] -> I{ClassName} (+ peer types if needed)  # S
        ...                                                             # S/C

