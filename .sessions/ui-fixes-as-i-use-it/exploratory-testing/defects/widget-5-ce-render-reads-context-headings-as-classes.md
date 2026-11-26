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
