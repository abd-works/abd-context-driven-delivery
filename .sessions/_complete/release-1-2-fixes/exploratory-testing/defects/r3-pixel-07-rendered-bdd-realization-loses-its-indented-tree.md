# A BDD realization tree in markdown renders flat: every state and observation starts at the left edge, so what nests in what cannot be read

**Charter:** Round 3 second pass, Pixel: how each file of the combined project is displayed (check 3).
**Tester:** Pixel

**Story:** Review Generated Work In File Viewer / View Files In Source View / "Render a markdown file as the page it describes". No scenario covers an indented tree. BDD's own guidance: "Every BDD artifact is an indented hierarchy."

**Module and class:** `harness/files_app/app/files/file-rendering.ts`, `renderingOf` (the other chat's Rendered / Source work, committed as aa23b0968).

**Severity:** wrong result: the nesting is what the file says, and the view it opens in drops it.

**Steps**
1. Stack `C:\dev\_et\round3\pixel\drv\stack.py` (cdd 8911, Files 8912) on the sandbox `C:\dev\_et\round3\pixel\work`; page `http://127.0.0.1:8912/?files=main&fidelity=<all fifteen fidelities>&project=C:\dev\_et\round3\pixel\work`, All session files pressed.
2. Press `bookshop-bdd-realization.md` (`.context/`). Its text nests two spaces a level: `a shipment`, under it `that has been created for a paid order`, under that a fenced call graph (`-> Cart.add(book: Book)`, `-> Order.pay(amount: number)`, `-> Shipment.books`, `it should list the order's books`), and under the state again `that has been dispatched`.

**Expected:** the tree with its levels, as Source shows it (or the file opened in Source, since it is a tree, not prose).

**Actual:** (`C:\dev\_et\round3\pixel\shots\w52-.context_bookshop-bdd-realization.md.png`) "a shipment", "that has been created for a paid order" and "that has been dispatched" all start at the left edge in one column; each call graph and its observation run together on one line of monospace: "-> Cart.add(book: Book) -> Order.pay(amount: number) -> Shipment.books it should list the order's books".

**Tier that should catch it:** unit, `files/file-rendering.spec.ts`, with an indented tree as an example.
