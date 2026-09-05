# Rule: Acceptance criteria are referenced, not copied

The wireframe does not embed AC text. The `mockup.md` affordance trace table cites the AC source file, story title, and clause number — reviewers read the original file. Do not paraphrase, shorten, or inline AC clauses into the wireframe or the markdown.

**DO** link each affordance row in the trace table to the exact AC story and clause number.

**DO NOT** copy AC text into `mockup.md` or into any wireframe label.

**DO NOT** skip a clause because it "overlaps" with another. Each clause has distinct conditions; cite each one separately.

**Example (pass):** Affordance trace row — `Continue button | Prompt for Game Directory if Invalid | AC 2 — saves path and continues startup if validation passes`

**Example (fail):** Inlining "WHEN the GM submits a path THEN the system re-validates it..." into the markdown. The AC source file is the authority; this file only points to it.
