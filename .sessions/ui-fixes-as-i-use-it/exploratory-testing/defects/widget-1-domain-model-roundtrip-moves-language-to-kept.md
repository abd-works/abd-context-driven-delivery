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
