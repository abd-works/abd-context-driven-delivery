# widget-5: Rendering pml-web's domain model (front matter `artifact: [ce-domain-model]`) with clean-engineering-model draws 6 cards named after its `##` headings ("Layout", "Customer", "Revenue", "Coverage"…), each holding the members of a dozen classes, and no arrows; ddd-model draws the 40 classes and 53 arrows

- **Charter:** C4
- **Tester:** Widget
- **Story:** no scenario covers which practice reads a `## context / ### aggregate / #### Class` model. Promise: `clean_engineering.md` model fidelity, "The same classes, operations, and relationships must appear in every selected representation"; the file's own front matter says it is a Clean Engineering domain model extending `practices/clean_engineering/templates/class-model.md`.
- **Module and class:** the Clean Engineering markdown model reader (`cdd_guidance/practices/clean_engineering/model/markdown/…`, reached through `PracticeFormats.render` / `parse`), which takes each `##` as a class and folds every `####` class below into it.
- **Severity:** wrong result (a board or diagram that looks finished but is wrong; nothing warns)

## Steps

1. Copy `test-area/pml-web` to a throwaway folder; `git init`.
2. With a throwaway `CDD_HOME`, from `C:\dev\abd-cdd-ui-fixes-as-i-use-it`:
   ```python
   r = Render().for_call(ToolCall({}, ROOT))
   r.render("clean-engineering-model", format="whiteboard", paths=["src/.context/domain-model.md"], source="markdown")
   r.render("clean-engineering-model", format="drawio", paths=["src/.context/domain-model.md"], source="markdown")
   ```
3. Count the elements of `domain-model.whiteboard` and the cells of `domain-model.drawio`; then do the same with `"ddd-model"`.

## Expected

The same classes and relationships whichever of the two practices draws it (both write the "CleanEngineering Model" page), or a refusal naming the layout the reader cannot read.

## Actual

clean-engineering-model: whiteboard `{'shape': 6, 'text': 1}`, no arrow; drawio 6 objects, 0 edges. The cards are `**Layout**`, `**Customer**` (all of Credentials', CredentialsValidation's, PasswordReset's… members and every invariant of the context as `//` lines), `**Inventory**`, `**Revenue**` (148 lines), `**Changed from the existing model**`, `**Coverage**`, each titled `` `Domain Model — My Paradise` ``.
ddd-model: whiteboard 39 shapes, 15 containers, 53 arrows; drawio 40 class cards, 53 edges. The graph reads the file only for DDD (clean_engineering part holds no node), so a person choosing the practice the front matter names gets the wrong drawing with no warning.

## Tier that should catch it

Unit: a CE model render example over a model in the `## context / ### aggregate / #### Class` layout (pml-web's), expecting its classes, or a refusal.

## Also seen by

## Triage

- **Status:** confirmed
- **Severity:** wrong result (a drawing that looks finished, silently wrong)
- **Triaged by:** Quill
- **Why:** the layout is one the Clean Engineering model reader promises. pml-web's file is written after the DDD model template (`cdd_guidance/practices/ddd/templates/model.md`), whose front matter declares `artifact: [ce-domain-model]` and which says it *extends* `practices/clean_engineering/templates/class-model.md` with the same class notation, and DDD's model fidelity says "Call clean_engineering at **model**". The reader's own card document (`CardDocument`: `#` title, `##` module, `###` group, `####` card) and its round-trip fixture (`model/markdown/fixtures/domain-model.md`, "a trimmed copy of a pml-web domain model") already read this nesting, but only when the class name is bold (`#### **Cart**`). The DDD template names the class plainly (`#### Cart <<Aggregate Root>>`), so no heading counted as a card, the reader fell back to the plain `#` module / `##` class layout, and every `##` (Layout, Customer, Revenue, Coverage...) became a class holding a dozen classes' members. Reproduced on a copy of `test-area/pml-web/src/.context/domain-model.md`: 6 "classes" under one module.
- **Missing warning:** with the reader now reading both templates' layouts, pml-web's file no longer renders wrong. A document whose class headings are neither bold nor followed by a stereotype is still read in the plain `#`/`##` layout without a warning; I would treat that as a separate, smaller defect (refuse or warn when a file declaring a model artifact yields classes with no members while holding class-card member lines), not fixed here.


## Fix

- **Test (unit):** `cdd_guidance/practices/clean_engineering/model/markdown/domain_model_layout_spec.py` with fixture `model/markdown/fixtures/ddd-layout-domain-model.md` (a trimmed copy of pml-web's model in the DDD template layout: front matter, `## Layout` and `## Coverage` sections, plain `####` cards, a `**CredentialsRepository** «Repository»` block, a heading repository, language, invariants, `//` notes and `->` calls), plus the bookshop template layout with a `**CartRepository** «Repository»` block. 14 of its 16 examples seen failing at HEAD (run in a detached worktree); all 16 pass after the fix. Every unit spec under `practices/clean_engineering` and `practices/ddd` passes.
- **Fix:** `model/markdown/markdown_class_model.py`: a card heading is a bold class name or a plain name followed by its `<<Stereotypes>>`, so the DDD template's `## context / ### aggregate / #### Class` reads as modules and class cards; a card keeps its heading as written (`ClassHeading.bold`) and writes a constructor line only when it was read with one; a `**Name** «Repository»` block inside a card (`REPOSITORY_IN_ROOT`, now in `class_card.py` beside the card notation) is read as a class of its own, kept in place, and written back as a block when changed. `model/base_class_model.py`: a class written from a drawing takes back the **Invariants** list the drawing does not hold. Guidance (`clean_engineering.md`, model Guidance, "Write each class card under its heading") and template (`templates/class-model.md`, the repository block) name both layouts.
- **End to end** on a copy of pml-web's `src/.context/domain-model.md` through `Render().for_call(...)`: clean-engineering-model to drawio draws 55 cards and 51 arrows (was 6 and 0); whiteboard 55 shapes, 51 arrows; drawio back to markdown leaves the file byte for byte unchanged (was +1328/-574); python writes each repository (CartRepository, SubscriptionRepository...) as its own class.
- **Commit:** dfe41aa2a (one commit for widget-5, widget-1 and widget-8: one shared fix)
