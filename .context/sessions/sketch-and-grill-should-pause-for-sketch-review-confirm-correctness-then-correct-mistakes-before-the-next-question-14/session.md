# Session: sketch-and-grill-should-pause-for-sketch-review-confirm-correctness-then-correct-mistakes-before-the-next-question-14

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-14
- **goal:** Sketch and grill should pause for sketch review, confirm correctness, then correct mistakes before the next question
- **fidelities:** development
- **contexts:** sketch, grill_context

## Progress

- Added `Sketch.review_sketch` hard gate after every `save_sketch`: pause, confirm correctness, name/correct mistakes, only then ask the next grill question.
- Hard rule wired in sketch.md + sketch prose: save early, overwrite on regen, review after every save, never defer persistence/review.
- Carry-forward: named review mistakes must shape the next sketch (correct the model; do not regenerate as if they never happened).
- Grill: thinking-first questions, sketch-validation gate, batch similar questions; mistakes constrain later options.
- Vanilla BDD (50 examples) + agent BDD for review gate and grill validation/batching.
