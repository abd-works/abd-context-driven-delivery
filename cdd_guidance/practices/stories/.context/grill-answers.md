# Stories migration — grill decisions (2026-07-16)

## Generator
- Port to `cdd_guidance/practices/stories` as a practice (`Stories`, a `PracticeGuidance`) like BDD / Clean Engineering.
- `generate` / `render` / `validate` mean the same as for the other practices.
- Create/deepen via conversation + the grill and sketch actions.

## Fidelities
- `discovery → exploration → specification → engineering` (since renamed: the fidelities are story_map, scenarios, and acceptance_tests)
- Drop shaping (use sketch instead). Unmapped `* approx N–M …` gaps live in `templates/stories-sketch.md`, not a separate outline map template.

## Formats
- Defaults: discovery→markdown; exploration+→python (pytest).
- All formatters are peer channels on the same CLI (markdown, json, drawio, miro, python, typescript, java, javascript).
- AI generate templates: **md + py only** (same as Clean Engineering). Other languages via formats and `render`; shared runners live in `model/{lang}/seeds/`.

## Model & formatters
- Reuse existing `StoryNode` model and all formatters from `abd-skills/practices/stories/src/stories`.
- Package (now): `model/` with one folder per format, `rules/`, `templates/`, `_examples/`.
- Nested SubEpics are folders; leaf SubEpics are files; Story=class; Scenario=operation; actor/examples/increments/backgrounds stay first-class.

## Hybrid code shape
- Regeneratable: test flow + examples/data.
- Engineering adds write-once tier files (AI writes real production-calling code).
- Layout from story-class shape; regen/step-key discipline from spec+tier.

## Rules / scanners
- Rule prose tightened into `stories.md`; the rules that check it are in `practices/stories/rules/` and run on the story model loaded onto the graph.
- Cross-language: formats (py/ts/js/java/md/json/…) fill model fields; rules never branch on file extension.

## Scope
- Port story-specific pieces; leave assembler/`src/skill` behind.
- Leave `abd-skills/stories` in place (do not delete).

## Stories vs BDD
- Stories = acceptance (e2e / tier-layer); BDD = object tests.
