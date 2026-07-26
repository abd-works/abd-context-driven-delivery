"""BDD specs for modules-fidelity DrawIO channel (system-context style)."""

import sys
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect, have_len
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
)
from context_tools.clean_engineering.class_model.drawio_class_model import (
    DrawIOCleanEngineeringModel,
)
from context_tools.clean_engineering.class_model.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)

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


with description("DrawIO modules fidelity"):
    with context("render modules view from canonical modules"):
        with before.each:
            model = CleanEngineeringModel(name="HeroesHandbook", sequential_order=1)
            checks = Module(
                name="checks",
                sequential_order=1,
                description="Resolve checks.",
                seam_terms=["Trait", "Check"],
            )
            character = Module(
                name="character",
                sequential_order=2,
                description="Sheet ownership.",
                seam_terms=["Character", "ISource"],
                dependencies=["checks"],
            )
            model.modules.extend([checks, character])
            self.xml = DrawIOCleanEngineeringModel.render(model)

        with it("should use Modules Context diagram id"):
            expect(self.xml).to(contain('id="modules-context"'))

        with it("should render module names and seam bullets"):
            expect(self.xml).to(contain("checks"))
            expect(self.xml).to(contain("\u2022 Trait"))
            expect(self.xml).to(contain("character"))
            expect(self.xml).to(contain("\u2022 ISource"))

        with it("should not include stack/tech callouts"):
            expect("stack / tech" in self.xml).to(be_false)

        with it("should draw a dependency edge character → checks"):
            expect(self.xml).to(contain('source="character"'))
            expect(self.xml).to(contain('target="checks"'))

    with context("round-trip markdown → drawio → model"):
        with before.each:
            parsed = MarkdownCleanEngineeringModel.parse(_MODULES_MD)
            drawio = DrawIOCleanEngineeringModel.render(parsed)
            self.back = DrawIOCleanEngineeringModel.parse(drawio)

        with it("should recover both modules"):
            expect(self.back.modules).to(have_len(2))

        with it("should recover seam terms on checks"):
            checks = next(m for m in self.back.modules if m.name == "checks")
            expect(checks.seam_terms).to(contain("Trait"))
            expect(checks.seam_terms).to(contain("Check"))
            expect(checks.seam_terms).to(contain("CheckResult"))

        with it("should recover character → checks dependency"):
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

    with context("parse AI template modules.drawio"):
        with before.each:
            path = (
                _REPO_ROOT
                / "context_tools"
                / "clean_engineering"
                / "templates"
                / "modules.drawio"
            )
            self.model = DrawIOCleanEngineeringModel.parse(
                path.read_text(encoding="utf-8")
            )

        with it("should parse placeholder modules as modules view"):
            expect(self.model.modules).to(have_len(5))

        with it("should keep placeholder module path names"):
            expect(self.model.modules[0].name).to(contain("module/path"))

        with it("should wire four dependency edges toward the hub module"):
            with_deps = [m for m in self.model.modules if m.dependencies]
            expect(with_deps).to(have_len(4))

    with context("path nesting renders as containment"):
        with before.each:
            parsed = MarkdownCleanEngineeringModel.parse(_NESTED_POWERS_MD)
            parsed.name = "Heroes Handbook"
            self.xml = DrawIOCleanEngineeringModel.render(parsed, previous=None)

        with it("should put Effect on the powers parent cell"):
            expect(self.xml).to(contain('id="powers"'))
            expect(self.xml).to(contain("\u2022 Effect"))

        with it("should nest powers/attack inside powers"):
            expect(self.xml).to(contain('id="powers-attack"'))
            expect(self.xml).to(contain('parent="powers"'))

        with it("should style nested children with the child fill"):
            expect(self.xml).to(contain("fillColor=#dae8fc"))

        with it("should not invent a powers/effect submodule cell"):
            expect("powers/effect" in self.xml).to(be_false)
            expect('id="powers-effect"' in self.xml).to(be_false)

        with it("should omit child→parent dependency edge"):
            # attack → powers is containment; edge should not target powers from attack
            expect(self.xml).not_to(
                contain('source="powers-attack" target="powers"')
            )

    with context("typed class model still renders UML class diagram"):
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
            self.xml = DrawIOCleanEngineeringModel.render(model)

        with it("should use the class-diagram diagram id"):
            expect(self.xml).to(contain('id="CleanEngineering-model"'))

        with it("should not use Modules Context id"):
            expect("modules-context" in self.xml).to(be_false)

        with it("should render class members"):
            expect(self.xml).to(contain("owner"))
            expect(self.xml).to(contain("place_order"))
