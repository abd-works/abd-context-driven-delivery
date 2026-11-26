# Rendered markdown drops every class stereotype and generic type: `Cart <<Aggregate Root>> <<Entity>>` reads "Cart <> <>"

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / View File In Source View / Scenario "Render a markdown file as the page it describes" ("scenarios, story maps and domain models are read as pages"). No scenario covers a model's `<<stereotype>>` or `Collection<Cart>`.

**Module and class:** `harness/files_app/app/files/file-rendering.ts`, `renderingOf` (markdown through `marked`, then `DOMPurify.sanitize`). This file is the other chat's Rendered / Source work, committed as aa23b0968; the checkout held no uncommitted change to it when I ran.

**Severity:** wrong result. The page a person reads a domain model or class model on, by default, leaves out what kind each class is and what each collection holds, with nothing saying text was removed.

**Steps**
1. Sandbox `C:\dev\_et\round3\pixel\work` (copy of the combined Bookshop), cdd server 8911, Files server 8912 (`C:\dev\_et\round3\pixel\drv\stack.py`).
2. Open `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen>&project=C:\dev\_et\round3\pixel\work`, press All session files, press `domain-model.md` (`.context/domain-model.md`). It opens Rendered.
3. Compare with Source. The same on `src/catalogue/.context/catalogue-model.md`, `fulfilment-model.md`, `ordering-model.md`.

**Expected:** the page shows the text the file holds: `Cart <<Aggregate Root>> <<Entity>>`, `CartRepository <<Repository>>`, `+ << aggregation >> carts: Collection<Cart>` (the notation of `practices/clean_engineering/templates/class-model.md`, which the file's front matter names).

**Actual:** (screenshot `C:\dev\_et\round3\pixel\shots\w17-.context_domain-model.md.png`)
- `#### Cart <<Aggregate Root>> <<Entity>>` reads **Cart <> <>**
- `#### CartRepository <<Repository>>` reads **CartRepository <>**; `CartLine <<Value Object>>` reads **CartLine <>**
- `+ << aggregation >> carts: Collection<Cart>` reads `<< aggregation >> carts: Collection`
`<Aggregate Root>`, `<Entity>`, `<Cart>` are read as HTML tags by marked and removed by DOMPurify. Source shows them whole.

**Tier that should catch it:** unit, `files/file-rendering.spec.ts`: its markdown examples hold a heading and a script, none holds text in angle brackets that is not a tag.
