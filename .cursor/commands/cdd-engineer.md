Run the action on cdd at engineer fidelity through the tools cli

Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd.
Call guidance on each stage child and pass that child to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

Provide guidance from contexts, examples, and templates.

# Contexts

## Stages (CDD fidelity)

| Fidelity | Intent | Default run scope |
|---|---|---|
| **discovery** | Whole-solution shape | Entire solution, or a large subsection |
| **explore** | Current increment | Increment, or a large subsection of it |
| **spec** | Narrow, concrete | ~sub-epic inside solution / increment |
| **engineer** | Working software | ~sub-epic inside solution / increment |

Grill and sketch work **much finer** inside that scope. Do not invent detail from a deeper stage.

### Stage → child fidelities

| CDD | stories | ddd | ux | clean_engineering | bdd |
|---|---|---|---|---|---|
| **discovery** | discovery | bounded_context | ia | modules | — |
| **explore** | exploration | building_blocks | mockup | model | **behavior** |
| **spec** | exploration | tactics | mockup | code | **development** |
| **engineer** | engineering | tactics | — | code | **development** |

UX has no engineering fidelity — production UI follows stories + clean_engineering at **engineer**, honouring the UX spec from **spec**.

### Sketch (one file)

Path: `{session.folder}/cdd-sketch.md` (see `templates/cdd-sketch.md`).

- **One file per engagement** — deepening fidelity (discovery → explore → spec → engineer) updates `fidelity:` at the top and deepens blocks in place. Never create a new file for a new fidelity.
- **Themes** — group lens blocks under one theme (epic, module, user goal, increment, or sub-epic).
- **`order-themes-by-journey`** — When the theme **is** the customer journey / epic, list themes in story-map experience order (Onboarding before Selfcare). Do not follow UX IA / sitemap order.
- **Beside each other** — lens blocks under a theme stay close and comparable; not separate files.
- **Flow** — after each chunk: more at this stage, or proceed. Recommend proceed only when views agree.
- **Trail** — `TODO` → `doing` → `pass #label` (or `skip #why`). Move passes to `## log` as `stage / scope / theme / …`.

### Rules

- **`stage-from-context`** — Infer CDD fidelity from workspace artifacts, sketch, and user intent; confirm when ambiguous.
- **`cdd-owns-grill-sketch`** — Grill and sketch at CDD level. When following a child `tools run`, skip nested child grill/sketch; apply the child generate body only.
- **`views-agree-before-proceed`** — Recommend proceed only when the views in play for the current scope agree; otherwise more at the same stage. User can override.
- **`todo-trail-in-sketch`** — Persist actions as TODO/doing/pass #label in the sketch; archive passes under `## log`.
- **`scaffold-before-content`** — **Hard gate.** Do not write `cdd-sketch.md` (or a file called `sketch.md`) until you have (1) **read** `templates/cdd-sketch.md` and each active child's `sketch_template` from `resolve_targets`, and (2) **AskQuestion** has confirmed which lenses are in play (`confirm-lenses-before-sketch`). Free prose instead of the scaffold is a defect.
- **`order-themes-by-journey`** — When the theme is the customer journey / epic, order themes by the story map / customer experience (Onboarding before Selfcare), not by UX IA.

---

## connect-story-examples/generate-interface-extensions/generate-type-extending-interface/generate_type_extending_interface_stories.py

"""Story data - regeneratable. Do not add logic or imports.

One story, three scenarios (Fake / Isolated / Production modes).
Owned by clean_engineering generator instructions/templates.
"""

from __future__ import annotations

from typing import Final


GENERATE_TYPE_EXTENDING_INTERFACE: Final = {
    "story": "Generate Type Extending Interface",
    "actor": "Generator",
    "domain_terms": (
        "IType",
        "Type",
        "TypeExampleFactory",
        "example_key",
        "mode",
    ),
    "evidence": (
        "cdd-sketch.md - Fake/Isolated/Production modes for any {Type}",
        "context_tools/clean_engineering - example factory pattern",
        "context_tools/cdd/example-factories - modes are not subclasses",
    ),

    "fake_mode_for_explore_spec": {
        "name": "fake mode for explore/spec",
        "given": (
            "an IType seam",
            "And examples[example_key] with field values for the types involved",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates TypeExampleFactory that builds IType in fake mode",
                ),
                "then": (
                    "the factory returns IType filled from examples[example_key]",
                    "And dependencies are not real collaborators",
                ),
            },
        ),
    },

    "isolated_mode_for_a_story_test_tier": {
        "name": "isolated mode for a story-test tier",
        "given": (
            "an IType seam",
            "And a tier test that must not pull the full stack",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates TypeExampleFactory that builds Type in isolated mode",
                ),
                "then": (
                    "the factory returns Type with ctor-injected mocks or stubs",
                    "And no FakeType / IsolatedType / ProductionType subclasses are emitted",
                ),
            },
        ),
    },

    "production_mode_for_a_story_test_tier": {
        "name": "production mode for a story-test tier",
        "given": (
            "an IType seam",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates TypeExampleFactory that builds Type in production mode",
                ),
                "then": (
                    "the factory returns Type with real collaborators",
                    "And tier tests can run against the production implementation",
                ),
            },
        ),
    },
}


## connect-story-examples/generate-interface-extensions/generate-type-extending-interface/generate_type_extending_interface_stories_spec.py

"""BDD spec for Generate Type Extending Interface story data (factory modes).
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_true, equal, expect
from mamba import before, context, description, it

from generate_type_extending_interface_stories import GENERATE_TYPE_EXTENDING_INTERFACE


with description("a generate-type-extending-interface story"):
    with context("that is loaded"):
        with before.each:
            self.story = GENERATE_TYPE_EXTENDING_INTERFACE

        with it("should name the story Generate Type Extending Interface"):
            expect(self.story["story"]).to(equal("Generate Type Extending Interface"))

        with it("should cast the Generator as actor"):
            expect(self.story["actor"]).to(equal("Generator"))

        with it("should include TypeExampleFactory and mode in domain terms"):
            terms = self.story["domain_terms"]
            expect("TypeExampleFactory" in terms).to(be_true)
            expect("mode" in terms).to(be_true)

        with it("should omit FakeType IsolatedType ProductionType subclass names"):
            terms = set(self.story["domain_terms"])
            expect("FakeType" in terms).to(equal(False))
            expect("IsolatedType" in terms).to(equal(False))
            expect("ProductionType" in terms).to(equal(False))

    with context("that describes factory modes"):
        with before.each:
            self.story = GENERATE_TYPE_EXTENDING_INTERFACE

        with it("should include a fake mode scenario"):
            expect("fake_mode_for_explore_spec" in self.story).to(be_true)

        with it("should include an isolated mode scenario"):
            expect("isolated_mode_for_a_story_test_tier" in self.story).to(be_true)

        with it("should include a production mode scenario"):
            expect("production_mode_for_a_story_test_tier" in self.story).to(be_true)

        with it("should state that FakeType subclasses are not emitted"):
            then_lines = self.story["isolated_mode_for_a_story_test_tier"][
                "interactions"
            ][0]["then"]
            joined = " ".join(then_lines)
            expect("FakeType" in joined and "subclasses are emitted" in joined).to(
                be_true
            )


## example-factories/example_factories.py

# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
"""Example factory seams at model fidelity - I{Class} only.

PATTERN: I{Type} / {Type} (production) / {Type}ExampleFactory.
Modes (not subclasses):
- Fake: mock/stub framework creates I{Type}; feed examples[{example_key}].
- Isolated: new {Type}(...ctor-injected mocks/stubs...).
- Production: new {Type}(...real collaborators...).
Factory methods load examples[{example_key}] multi-type bundles.
Explore/spec chain: steps -> helper -> factory -> fake I{Type}.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IType(ABC):
    """Public contract for a domain type filled from example bundles."""

    @abstractmethod
    def __init__(self) -> None: ...


class ICart(ABC):
    """Cart contract returned by cart example factory methods."""

    @abstractmethod
    def __init__(self) -> None: ...


class IProduct(ABC):
    """Product contract - often bundled with cart in the same example_key."""

    @abstractmethod
    def __init__(self) -> None: ...


class ICartExampleFactory(ABC):
    """Named factory methods for cart-related story examples."""

    @abstractmethod
    def cart_with_items(self, mode: str = "fake") -> tuple[ICart, IProduct]:
        """Load examples[cart_with_items] in fake | isolated | production mode -> ICart, IProduct."""
        ...


## example-factories/example_factories_spec.py

"""BDD spec for example factory seams — I{Type} contracts and factory modes.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import inspect
import sys
from abc import ABC
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_true, equal, expect, raise_error
from mamba import context, description, it

from example_factories import ICart, ICartExampleFactory, IProduct, IType


with description("an example factory seam"):
    with context("that exposes domain interfaces"):
        with it("should define IType as an abstract base"):
            expect(issubclass(IType, ABC)).to(be_true)
            expect(inspect.isabstract(IType)).to(be_true)

        with it("should define ICart as an abstract base"):
            expect(issubclass(ICart, ABC)).to(be_true)
            expect(inspect.isabstract(ICart)).to(be_true)

        with it("should define IProduct as an abstract base"):
            expect(issubclass(IProduct, ABC)).to(be_true)
            expect(inspect.isabstract(IProduct)).to(be_true)

        with it("should define ICartExampleFactory as an abstract base"):
            expect(issubclass(ICartExampleFactory, ABC)).to(be_true)
            expect(inspect.isabstract(ICartExampleFactory)).to(be_true)

    with context("whose cart factory method is inspected"):
        with it("should accept a mode parameter defaulting to fake"):
            params = inspect.signature(ICartExampleFactory.cart_with_items).parameters
            expect("mode" in params).to(be_true)
            expect(params["mode"].default).to(equal("fake"))

        with it("should refuse concrete instantiation without cart_with_items"):
            expect(lambda: ICartExampleFactory()).to(raise_error(TypeError))


Separate tools run — toolset: `context_tools.ddd.ddd:Ddd` action: `guidance` context.fidelity: `tactics`

Separate tools run — toolset: `context_tools.stories.stories:Stories` action: `guidance` context.fidelity: `acceptance_tests`

Separate tools run — toolset: `context_tools.ux.ux:Ux` action: `guidance` context.fidelity: `front_end_code`

Separate tools run — toolset: `context_tools.clean_engineering.clean_engineering:CleanEngineering` action: `guidance` context.fidelity: `code`

Separate tools run — toolset: `context_tools.bdd.bdd:Bdd` action: `guidance` context.fidelity: `development`

Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: engineer
tool: <tool name>
arguments:
  <if needed>
```

Run: python -m tools run -

Before following the suggested flow, display the tools made available to this chat in your user-visible reply — each tool name and what it is for. Do not only follow them silently or rediscover them by remanifesting.

Tools made available:
- guidance

Suggested flow (repeat and reorder as the story needs):

1. tool: guidance

2. tool: guidance

3. tool: guidance

4. tool: guidance

5. tool: guidance

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: engineer
action: generate
```
.\tools.ps1 run -
