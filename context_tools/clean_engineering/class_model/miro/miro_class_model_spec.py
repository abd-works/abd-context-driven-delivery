"""Mamba spec for `MiroCleanEngineeringModel`.

Mirrors context_tools/clean_engineering/class_model/drawio/drawio_module_model_spec.py
one-for-one, substituting SVG/Mermaid assertions for XML/mxCell assertions.

Two description blocks (one per fidelity, one turn each):
  1. modules fidelity  — flowchart Mermaid: modules + deps + nesting
  2. class fidelity    — classDiagram Mermaid: classes + properties + ops + rels
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mamba import description, context, it, before
from expects import be_false, be_true, contain, equal, expect, have_len

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from context_tools.clean_engineering.class_model.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)
from context_tools.clean_engineering.class_model.miro.miro_class_model import (
    MiroCleanEngineeringModel,
)


# ---------------------------------------------------------------------------
# Shared fixtures (identical to drawio_module_model_spec.py markdown snippets)
# ---------------------------------------------------------------------------

_MODULES_MD = """\
# checks

Foundation check resolution.

- **Purpose:** Resolve d20 + trait against difficulty.
- **Seam (terms):** Trait, Check, CheckResult
- **Dependencies (one-way):** *(none)*

# character

Owns the hero sheet and ISource.

- **Purpose:** Character sheet ownership and ISource.
- **Seam (terms):** Character, Ability, ISource
- **Dependencies (one-way):** checks
"""

_NESTED_POWERS_MD = """\
# powers

Owns Effect shared base.

- **Purpose:** Shared Effect seam on the parent.
- **Seam (terms):** Effect
- **Dependencies (one-way):** character, checks

# powers/attack

Attack-typed effects.

- **Purpose:** Specialize Effect for attack-type powers.
- **Seam (terms):** AttackEffect
- **Dependencies (one-way):** powers, checks

# checks

Foundation.

- **Purpose:** Resolve checks.
- **Seam (terms):** Trait, Check
- **Dependencies (one-way):** *(none)*

# character

Sheet.

- **Purpose:** Sheet ownership.
- **Seam (terms):** Character, ISource
- **Dependencies (one-way):** checks
"""

_NESTED_MODULE_CONTEXT_MD = """\
# powers/effect

Shared base for all power effects.

## Modules fidelity

### Module `powers/effect`

- **Purpose:** Own the shared Effect seam.
- **Seam (terms):** Effect
- **Dependencies (one-way):** `character`, `checks`
- **Build order:** see module-build-order.md
"""


def _extract_mermaid(svg_text: str) -> str:
    """Pull the Mermaid source out of the canvas-composer SVG."""
    root = ET.fromstring(
        svg_text.split("\n", 1)[1] if svg_text.startswith("<?") else svg_text
    )
    for el in root.iter():
        tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
        if tag == "foreignObject" and el.get("data-type") == "diagram":
            return (el.text or "").strip()
    return ""


def _extract_diagrams(svg_text: str):
    """Return every Miro diagram widget and its Mermaid source."""
    root = ET.fromstring(
        svg_text.split("\n", 1)[1] if svg_text.startswith("<?") else svg_text
    )
    return [
        (el, (el.text or "").strip())
        for el in root.iter()
        if el.tag.split("}")[-1] == "foreignObject"
        and el.get("data-type") == "diagram"
    ]


def _shop_model(
    extra_properties=None,
    extra_class: Optional[OoadClass] = None,
    extra_relationship: Optional[Relationship] = None,
) -> CleanEngineeringModel:
    model = CleanEngineeringModel(name="Shop", sequential_order=1)
    module = Module(name="Shop", sequential_order=1)
    cart_props = [Property(name="owner", type_hint="str")]
    if extra_properties:
        cart_props.extend(extra_properties)
    cart_rels = [Relationship(target="Order", kind="association")]
    if extra_relationship:
        cart_rels.append(extra_relationship)
    module.classes.append(
        OoadClass(
            name="Cart",
            sequential_order=1,
            properties=cart_props,
            operations=[Operation(name="place_order", return_type="Order")],
            relationships=cart_rels,
        )
    )
    module.classes.append(
        OoadClass(
            name="Order",
            sequential_order=2,
            properties=[Property(name="total", type_hint="int")],
        )
    )
    if extra_class is not None:
        module.classes.append(extra_class)
    model.modules.append(module)
    return model


# ===========================================================================
# Turn 4 — modules fidelity
# ===========================================================================

with description("MiroCleanEngineeringModel modules fidelity") as self:

    with context("render modules view from canonical modules"):
        with before.each:
            model = CleanEngineeringModel(name="HeroesHandbook", sequential_order=1)
            checks = Module(
                name="checks", sequential_order=1,
                description="Resolve checks.",
                seam_terms=["Trait", "Check"],
            )
            character = Module(
                name="character", sequential_order=2,
                description="Sheet ownership.",
                seam_terms=["Character", "ISource"],
                dependencies=["checks"],
            )
            model.modules.extend([checks, character])
            self.svg = MiroCleanEngineeringModel.render(model)
            self.mermaid = _extract_mermaid(self.svg)

        with it("should produce a valid canvas-composer SVG with a diagram foreignObject"):
            root = ET.fromstring(
                self.svg.split("\n", 1)[1] if self.svg.startswith("<?") else self.svg
            )
            fo = None
            for el in root.iter():
                tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
                if tag == "foreignObject" and el.get("data-type") == "diagram":
                    fo = el
                    break
            expect(fo is not None).to(be_true)

        with it("should produce a Mermaid flowchart diagram"):
            expect(self.mermaid.startswith("flowchart")).to(be_true)

        with it("should render module names and seam bullets in the Mermaid source"):
            expect("checks" in self.mermaid).to(be_true)
            expect("\u2022 Trait" in self.mermaid).to(be_true)
            expect("character" in self.mermaid).to(be_true)
            expect("\u2022 ISource" in self.mermaid).to(be_true)

        with it("should not include stack/tech callouts"):
            expect("stack / tech" in self.mermaid).to(be_false)

        with it("should draw a dependency edge character -> checks"):
            expect("character --> checks" in self.mermaid).to(be_true)

    with context("round-trip markdown -> miro -> model"):
        with before.each:
            parsed = MarkdownCleanEngineeringModel.parse(_MODULES_MD)
            svg = MiroCleanEngineeringModel.render(parsed)
            self.back = MiroCleanEngineeringModel.parse(svg)

        with it("should recover both modules"):
            expect(self.back.modules).to(have_len(2))

        with it("should recover seam terms on checks"):
            checks = next(m for m in self.back.modules if m.name == "checks")
            expect(checks.seam_terms).to(contain("Trait"))
            expect(checks.seam_terms).to(contain("Check"))
            expect(checks.seam_terms).to(contain("CheckResult"))

        with it("should recover character -> checks dependency"):
            character = next(m for m in self.back.modules if m.name == "character")
            expect(character.dependencies).to(contain("checks"))

        with it("should leave checks with no dependencies"):
            checks = next(m for m in self.back.modules if m.name == "checks")
            expect(checks.dependencies).to(equal([]))

    with context("parse nested Modules fidelity markdown section"):
        with before.each:
            self.model = MarkdownCleanEngineeringModel.parse(_NESTED_MODULE_CONTEXT_MD)

        with it("should parse the module path name"):
            expect(self.model.modules).to(have_len(1))
            expect(self.model.modules[0].name).to(equal("powers/effect"))

        with it("should parse seam terms from the Modules fidelity block"):
            expect(self.model.modules[0].seam_terms).to(equal(["Effect"]))

        with it("should parse one-way dependencies"):
            expect(self.model.modules[0].dependencies).to(
                equal(["character", "checks"])
            )

    with context("path nesting renders as containment"):
        with before.each:
            parsed = MarkdownCleanEngineeringModel.parse(_NESTED_POWERS_MD)
            parsed.name = "Heroes Handbook"
            self.svg = MiroCleanEngineeringModel.render(parsed, previous=None)
            self.mermaid = _extract_mermaid(self.svg)

        with it("should put the powers module in the Mermaid source"):
            expect("powers" in self.mermaid).to(be_true)
            expect("\u2022 Effect" in self.mermaid).to(be_true)

        with it("should nest powers/attack inside a powers subgraph"):
            expect("subgraph powers" in self.mermaid).to(be_true)
            expect("powers_attack" in self.mermaid).to(be_true)

        with it("should not invent a powers/effect submodule node"):
            expect("powers_effect" in self.mermaid).to(be_false)
            expect("powers/effect" in self.mermaid).to(be_false)

        with it("should omit child->parent dependency edge"):
            # powers/attack -> powers is containment; no arrow from attack to powers
            expect("powers_attack --> powers" in self.mermaid).to(be_false)


# ===========================================================================
# Turn 5 — class fidelity
# ===========================================================================

with description("MiroCleanEngineeringModel class fidelity") as self:

    with context("typed class model renders UML class diagram"):
        with before.each:
            model = CleanEngineeringModel(name="Shop", sequential_order=1)
            module = Module(name="Shop", sequential_order=1)
            module.classes.append(
                OoadClass(
                    name="Cart",
                    sequential_order=1,
                    properties=[Property(name="owner", type_hint="str")],
                    operations=[Operation(name="place_order", return_type="Order")],
                )
            )
            model.modules.append(module)
            self.svg = MiroCleanEngineeringModel.render(model)
            self.mermaid = _extract_mermaid(self.svg)

        with it("should produce a Mermaid classDiagram"):
            expect(self.mermaid.startswith("classDiagram")).to(be_true)

        with it("should not produce a Modules Context flowchart"):
            expect(self.mermaid.startswith("flowchart")).to(be_false)

        with it("should render class members"):
            expect("owner" in self.mermaid).to(be_true)
            expect("place_order" in self.mermaid).to(be_true)

    with context("round-trip class model -> miro -> model"):
        with before.each:
            self.original = _shop_model()
            svg = MiroCleanEngineeringModel.render(self.original)
            self.back = MiroCleanEngineeringModel.parse(svg)

        with it("should recover the Cart class"):
            all_classes = list(self.back.classes)
            cart = next((c for c in all_classes if c.name == "Cart"), None)
            expect(cart is not None).to(be_true)

        with it("should recover Cart properties"):
            all_classes = list(self.back.classes)
            cart = next(c for c in all_classes if c.name == "Cart")
            prop_names = [p.name for p in cart.properties]
            expect("owner" in prop_names).to(be_true)

        with it("should recover Cart operations"):
            all_classes = list(self.back.classes)
            cart = next(c for c in all_classes if c.name == "Cart")
            op_names = [o.name for o in cart.operations]
            expect("place_order" in op_names).to(be_true)

        with it("should recover Cart -> Order association"):
            all_classes = list(self.back.classes)
            cart = next(c for c in all_classes if c.name == "Cart")
            expect(any(r.target == "Order" for r in cart.relationships)).to(be_true)

    with context("new relationship renders with the correct Mermaid arrow"):
        with before.each:
            model = _shop_model(
                extra_relationship=Relationship(target="Order", kind="composition")
            )
            self.svg = MiroCleanEngineeringModel.render(model)
            self.mermaid = _extract_mermaid(self.svg)

        with it("should use the *-- composition arrow"):
            expect("*--" in self.mermaid).to(be_true)

    with context("inheritance relationship renders with the <|-- arrow"):
        with before.each:
            model = _shop_model(
                extra_relationship=Relationship(target="Order", kind="inheritance")
            )
            self.svg = MiroCleanEngineeringModel.render(model)
            self.mermaid = _extract_mermaid(self.svg)

        with it("should use the <|-- inheritance arrow"):
            expect("<|--" in self.mermaid).to(be_true)

    with context("a decorated model split across source modules"):
        with before.each:
            model = CleanEngineeringModel(name="Paradise Mobile", sequential_order=1)
            customer = Module(name="Customer — abstract base", sequential_order=1)
            customer.classes.extend([
                OoadClass(
                    name="**Customer** <<Abstract>> <<Entity>>",
                    sequential_order=1,
                    properties=[Property(name="identity", type_hint="Identity")],
                    relationships=[Relationship(target="Identity", kind="composition")],
                ),
                OoadClass(name="**Identity** <<Entity>>", sequential_order=2),
            ])
            prospect = Module(name="Prospect — onboarding", sequential_order=2)
            prospect.classes.append(
                OoadClass(
                    name="**Prospect** <<Aggregate Root>> <<Entity>> extends Customer",
                    sequential_order=1,
                    operations=[
                        Operation(
                            name="selectPlan",
                            parameters=["plan: Plan"],
                            return_type="AccountCredentials",
                        )
                    ],
                )
            )
            model.modules.extend([customer, prospect])
            self.svg = MiroCleanEngineeringModel.render(model)
            self.diagrams = _extract_diagrams(self.svg)
            self.by_module = {
                element.get("data-module"): mermaid
                for element, mermaid in self.diagrams
            }

        with it("should create one Miro diagram widget for every source module"):
            expect(self.diagrams).to(have_len(2))
            expect(set(self.by_module)).to(
                equal({"Customer — abstract base", "Prospect — onboarding"})
            )

        with it("should place widgets left to right beyond their rendered overflow"):
            positions = [
                (int(element.get("x")), int(element.get("y")))
                for element, _ in self.diagrams
            ]
            expect(positions).to(equal([(1000, 2000), (4500, 2000)]))

        with it("should keep local classes on their owning module diagram"):
            expect(
                "%% local: Customer" in self.by_module["Customer — abstract base"]
            ).to(be_true)
            expect(
                "%% local: Prospect" in self.by_module["Prospect — onboarding"]
            ).to(be_true)
            expect(
                "%% local: Prospect" in self.by_module["Customer — abstract base"]
            ).to(be_false)

        with it("should show cross-module inheritance participants as imports"):
            expect(
                "%% imported: Prospect" in self.by_module["Customer — abstract base"]
            ).to(be_true)
            expect(
                "%% imported: Customer" in self.by_module["Prospect — onboarding"]
            ).to(be_true)

        with it("should use plain Mermaid identifiers and separate UML stereotypes"):
            customer_diagram = self.by_module["Customer — abstract base"]
            expect("class Customer {" in customer_diagram).to(be_true)
            expect("class **Customer**" in customer_diagram).to(be_false)
            expect("<<Abstract>>" in customer_diagram).to(be_true)
            expect("<<Entity>>" in customer_diagram).to(be_true)

        with it("should derive inheritance from an extends clause"):
            expect(
                "Customer <|-- Prospect" in self.by_module["Prospect — onboarding"]
            ).to(be_true)

        with it("should preserve operation parameters in the class member"):
            expect(
                "+selectPlan(plan: Plan) AccountCredentials"
                in self.by_module["Prospect — onboarding"]
            ).to(be_true)

        with it("should restore source module boundaries without imported duplicates"):
            parsed = MiroCleanEngineeringModel.parse(self.svg)
            expect([module.name for module in parsed.modules]).to(
                equal(["Customer — abstract base", "Prospect — onboarding"])
            )
            expect([c.name for c in parsed.modules[0].classes]).to(
                equal(["Customer", "Identity"])
            )
            expect([c.name for c in parsed.modules[1].classes]).to(equal(["Prospect"]))
