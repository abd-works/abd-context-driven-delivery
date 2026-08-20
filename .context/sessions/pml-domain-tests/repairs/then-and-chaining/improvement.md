# then-and-chaining

- **tool:** Stories
- **error:** Extra outcomes were emitted as another `then()`, so the Gherkin narrative broke and the DSL's chain return was ignored.
- **rule:** then-and-chaining
- **what changed:**
  - **Prose — yes.** `stories.md` (scenarios + acceptance_tests): first outcome `then()`; later outcomes `.and()`. Markdown `And` stays `And`.
  - **Sketch / template / example — yes.** `stories-sketch.md` Then/And; TS/JS `{story}_story` templates chain `.and()`.
  - **Detector — no.**
  - **Generator — yes.** TypeScript (and JS) `story_file.py` emits one `then()` then `.and()` per extra Then clause. Seed `story-test.ts` returns a `ThenChain` with `.and()`.
