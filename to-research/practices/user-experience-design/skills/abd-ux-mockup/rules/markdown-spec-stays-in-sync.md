# `mockup.md` stays in sync with the wireframe

The markdown spec and the `.drawio` wireframe are two views of the same mockup pass. They must agree at every commit.

**DO** author or update `mockup.md` **before** regenerating the wireframe. The markdown carries the scope, the regions, the interaction decisions, and the affordance-trace column. The wireframe is generated from the state file, which is driven by the markdown.

**DO** read the updated wireframe after regeneration and reflect any manual Draw.io edits (renamed control, control moved between regions, added region, changed label) back into `mockup.md` in the same run — including the affordance-trace column.

**DO** append a row to the change log in `mockup.md` every time the wireframe changes, recording date, direction (`md → drawio` or `drawio → md`), and a one-line summary.

**DO NOT** commit a `.drawio` whose regions, controls, or labels disagree with `mockup.md`. If they disagree, decide which is right, fix the other, then commit.

**DO NOT** let domain term labels drift in `mockup.md`. Re-read from the source domain terms file if there is any doubt — verbatim rules apply to the markdown the same way they apply to the wireframe controls.
