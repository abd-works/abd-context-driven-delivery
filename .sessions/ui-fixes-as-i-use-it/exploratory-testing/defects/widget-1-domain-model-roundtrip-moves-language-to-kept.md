# widget-1: Rendering pml-web's domain model to drawio and straight back to markdown rewrites the whole file: every class, aggregate and context paragraph, invariant, `//` comment, `->` interaction and repository block moves below "Kept from this file", and the front matter becomes plain paragraphs

- **Charter:** C4 (diagrams, story explorer, scenario reader)
- **Tester:** Widget
- **Story:** no scenario covers a round trip of a `## context / ### aggregate / #### Class` model. Closest promise: `cdd_guidance/practices/clean_engineering/clean_engineering.md` model fidelity: "The same classes, operations, and relationships must appear in every selected representation", and "Open each class card with its language".
- **Module and class:** `harness/guidance/practice_formats.py` `PracticeFormats.render` (the drawing's kept document goes to the markdown writer as `previous`); the clean engineering markdown writer, which keeps nothing of a file in this layout; `cdd_guidance/actions/render/kept_document.py` `KeptDocument._markdown`, which then puts every original line below the rendered text.
- **Severity:** wrong result (the person's file is rewritten without any change on the drawing; nothing is deleted, but all of the language is pushed into a 1400-line "Kept" tail that they have to move back by hand).

## Steps

1. Copy `test-area/pml-web` into a throwaway folder and `git init` it.
2. With `CDD_HOME` throwaway, `PYTHONUTF8=1`, from `C:\dev\abd-cdd-ui-fixes-as-i-use-it`:
   ```python
   from cdd_guidance.actions.render.render import Render
   from harness.agent_tools.tool_call import ToolCall
   r = Render().for_call(ToolCall({}, ROOT))
   r.render("ddd-model", format="drawio", paths=["src/.context/domain-model.md"], source="markdown")   # draws the CleanEngineering Model page
   r.render("clean-engineering-model", format="markdown", paths=["src/.context/domain-model.drawio"], source="drawio")
   ```
   (no edit to the drawing in between)
3. `git diff --stat src/.context/domain-model.md`

## Expected

The same file back, or at most the members the drawing changed: the drawing keeps the whole source document (`cddSourceDocument`), and the same round trip on the bookshop fixture (`cdd_guidance/practices/clean_engineering/model/fixtures/bookshop/ordering-model.md`, `# module / ## group / ### **Class**`) gives back the file byte for byte.

## Actual

`1328 insertions(+), 574 deletions(-)`. The file now opens `# Customer · Credentials` / `## Credentials <<Aggregate Root>> <<Entity>>`; no front matter (the lines `fidelity: [model]`, `artifact: [ce-domain-model]`, `format: md` sit as paragraphs under `## Kept from this file, no longer in the model`); each class gains a constructor the file says it leaves out ("Constructors are left out of this view"); the context and aggregate paragraphs ("Who the customer is and how they sign in…", "The email and password a customer signs in with…"), every **Invariants** list, every `// Access Selfcare` comment and every `-> CredentialsRepository.create(this)` interaction are gone from the model part and only in the Kept tail. The repository classes drawn inside their root's card (CredentialsRepository and the others) are not read back as classes at all: the regenerated model names `CredentialsRepository` only as a return type.

## Tier that should catch it

Unit: a render_spec example rendering a model in the `## context / ### aggregate / #### Class` layout with a `**XRepository** «Repository»` block to drawio and back, expecting the file unchanged. The existing round-trip examples use only the bookshop/template layout, which survives.

## Also seen by

## Triage

- **Status:** confirmed
- **Severity:** wrong result (the person's file rewritten with no change on the drawing)
- **Triaged by:** Quill
- **Why:** same root cause as widget-5: the Clean Engineering markdown reader did not take pml-web's plain `#### Class <<Stereotype>>` headings (the DDD model template's layout, artifact `ce-domain-model`, which extends the Clean Engineering class-model template) as class cards, so it read nothing it could write back in place, and `KeptDocument` put the whole file under "Kept from this file". Two further losses showed once the cards were read: the drawing carries no **Invariants** list, and the translation from the drawing cleared each class's invariants (the words a drawing does not hold were taken back from the document for the intent and members, not the invariants); and a changed card gained a constructor line the card never wrote. The repository blocks are widget-8.


## Fix

- **Test (unit):** `cdd_guidance/practices/clean_engineering/model/markdown/domain_model_layout_spec.py` with fixture `model/markdown/fixtures/ddd-layout-domain-model.md` (a trimmed copy of pml-web's model in the DDD template layout: front matter, `## Layout` and `## Coverage` sections, plain `####` cards, a `**CredentialsRepository** «Repository»` block, a heading repository, language, invariants, `//` notes and `->` calls), plus the bookshop template layout with a `**CartRepository** «Repository»` block. 14 of its 16 examples seen failing at HEAD (run in a detached worktree); all 16 pass after the fix. Every unit spec under `practices/clean_engineering` and `practices/ddd` passes.
- **Fix:** `model/markdown/markdown_class_model.py`: a card heading is a bold class name or a plain name followed by its `<<Stereotypes>>`, so the DDD template's `## context / ### aggregate / #### Class` reads as modules and class cards; a card keeps its heading as written (`ClassHeading.bold`) and writes a constructor line only when it was read with one; a `**Name** «Repository»` block inside a card (`REPOSITORY_IN_ROOT`, now in `class_card.py` beside the card notation) is read as a class of its own, kept in place, and written back as a block when changed. `model/base_class_model.py`: a class written from a drawing takes back the **Invariants** list the drawing does not hold. Guidance (`clean_engineering.md`, model Guidance, "Write each class card under its heading") and template (`templates/class-model.md`, the repository block) name both layouts.
- **End to end** on a copy of pml-web's `src/.context/domain-model.md` through `Render().for_call(...)`: clean-engineering-model to drawio draws 55 cards and 51 arrows (was 6 and 0); whiteboard 55 shapes, 51 arrows; drawio back to markdown leaves the file byte for byte unchanged (was +1328/-574); python writes each repository (CartRepository, SubscriptionRepository...) as its own class.
- **Commit:** see below.
