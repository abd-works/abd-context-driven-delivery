# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for RecipeGuide - demonstrates all three @instruction forms."""
import sys
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.instructions.instructions import _instruction_ref_resolves
from primitives.instructions import instruction_slot_names
from primitives.instructions.examples.recipe_guide.recipe_guide import RecipeGuide


with description("RecipeGuide"):
    with context("that has been created with a cuisine"):
        with before.each:
            self.guide = RecipeGuide(cuisine="French")

        with it("should expose the cuisine via the cuisine property"):
            expect(self.guide.cuisine).to(equal("French"))

        with it("should start with a draft count of zero"):
            expect(self.guide.draft_count).to(equal(0))


with description("RecipeGuide add_draft tool"):
    with context("that saves a recipe draft"):
        with before.each:
            self.guide = RecipeGuide(cuisine="Japanese")

        with it("should return a confirmation message"):
            result = self.guide.add_draft(recipe="Miso soup")
            expect(result).to(equal("Draft saved: Miso soup"))

        with it("should increment draft_count after saving"):
            self.guide.add_draft(recipe="Miso soup")
            expect(self.guide.draft_count).to(equal(1))


with description("RecipeGuide read_drafts tool"):
    with context("when no drafts have been saved"):
        with before.each:
            self.guide = RecipeGuide(cuisine="Mexican")

        with it("should return a no-drafts message"):
            expect(self.guide.read_drafts()).to(equal("No drafts yet."))

    with context("when one or more drafts have been saved"):
        with before.each:
            self.guide = RecipeGuide(cuisine="Mexican")
            self.guide.add_draft(recipe="Tacos al pastor")
            self.guide.add_draft(recipe="Enchiladas verdes")

        with it("should return a numbered list of drafts"):
            result = self.guide.read_drafts()
            expect(result).to(contain("1. Tacos al pastor"))
            expect(result).to(contain("2. Enchiladas verdes"))


with description("RecipeGuide technique instruction slot"):
    with context("declared on the class"):
        with it("should be marked as an instruction slot"):
            expect(getattr(RecipeGuide.technique, "_is_instruction_slot", False)).to(be_true)

        with it("should resolve to the Technique section in recipe_guide.md"):
            guide = RecipeGuide(cuisine="French")
            expect(_instruction_ref_resolves(guide, "technique")).to(be_true)

    with context("when expanded on a live instance"):
        with it("should include mise en place guidance"):
            guide = RecipeGuide(cuisine="French")
            from primitives.instructions import _inline
            result = _inline(guide, "technique")
            expect(len(result) > 0).to(be_true)
            expect(result.lower()).to(contain("mise en place"))


with description("RecipeGuide plating instruction slot"):
    with context("declared on the class with label='plating-rules'"):
        with it("should be marked as an instruction slot"):
            expect(getattr(RecipeGuide.plating, "_is_instruction_slot", False)).to(be_true)

        with it("should resolve to the plating-rules.md file"):
            guide = RecipeGuide(cuisine="French")
            expect(_instruction_ref_resolves(guide, "plating-rules")).to(be_true)

    with context("when expanded on a live instance"):
        with it("should include plate and sauce guidance"):
            guide = RecipeGuide(cuisine="French")
            from primitives.instructions import _inline
            result = _inline(guide, "plating")
            expect(len(result) > 0).to(be_true)
            expect(result.lower()).to(contain("plate"))


with description("RecipeGuide brainstorm action"):
    with context("declared on the class"):
        with it("should be marked as an action"):
            expect(getattr(RecipeGuide.brainstorm, "_is_agent_instructions", False)).to(be_true)


with description("RecipeGuide draft_recipe action"):
    with context("declared on the class"):
        with it("should be marked as an action"):
            expect(getattr(RecipeGuide.draft_recipe, "_is_agent_instructions", False)).to(be_true)


with description("RecipeGuide instruction_slot_names"):
    with context("inspecting the class"):
        with it("should include technique and plating"):
            names = instruction_slot_names(RecipeGuide)
            expect("technique" in names).to(be_true)
            expect("plating" in names).to(be_true)
