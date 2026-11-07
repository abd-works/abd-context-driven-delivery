# cdd_guidance/practices/ux/story-demo
*Story Demo* runs a mockup against its stories in the browser, so a person can watch a story play through the screens or drive the screens themselves. `StoryDemoPage.load(createStory, mode)` loads a story into the page in one of two modes: *Play*, where the explorer steps through the story's scenarios with `playNext`, and *Interactive*, where using a *StoryDemoControl* runs the story steps attached to it. The mockup's HTML marks which controls, lists, and inputs take part through `data-` attributes the generated mockup already writes.

*PlayDualRunner* collects a story's Given/When/Then steps and plays them one at a time in the browser, reporting a failed Then without stopping the page. `story-test-core` defines stories with `story`, `scenario`, and `collect` in a form that runs both in the browser and under Node's test runner (`story-test-node`), and `soft-assert` gives browser-safe Then assertions.

- **Purpose:** Show a mockup working through its stories, step by step or by hand, without a backend.
- **Seam (terms):** StoryDemoPage, PlayDualRunner, StoryDemoControl, `story-test-core`, `story-test-node`, `soft-assert`
- **Dependencies (one-way):** `cdd_guidance/practices/ux/model` (*StoryDemoControl*, which the HTML mockup is rendered from)

## Constraint

A plain *Control* has no story steps; only a *StoryDemoControl* runs them. A mockup's HTML imports `story-test-core` only, never the Node backend, so it runs in the browser. Keep the domain objects a story exposes across story switches in the page's session, and reset clears them.
