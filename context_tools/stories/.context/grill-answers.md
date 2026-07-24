# Stories migration — grill decisions (2026-07-16)

## Generator
- Port to `abd-context-driven-delivery/stories` as a `@context` like BDD / Clean Engineering.
- `generate` / `transform` / `validate` mean the same as other generators.
- Create/deepen via conversation + `@grill_with_context` + `@sketch`.

## Fidelities
- `discovery → exploration → specification → engineering`
- Drop shaping (use sketch instead). Unmapped `* approx N–M …` gaps live in `sketch-template.md`, not a separate outline map template.

## Formats
- Defaults: discovery→markdown; exploration+→python (pytest).
- All formatters are peer channels on the same CLI (markdown, json, drawio, miro, python, typescript, java, javascript).
- AI generate templates: **md + py only** (same as Clean Engineering). Other langs via channels/`transform`; shared runners live in `code/{lang}/seeds/`.

## Model & formatters
- Reuse existing `StoryNode` model and all formatters from `abd-skills/context_tools/stories/src/stories`.
- Package: `story_model/`, `document/`, `diagram/`, `code/`, `scanners/`, `examples/`.
- Nested SubEpics are folders; leaf SubEpics are files; Story=class; Scenario=operation; actor/examples/increments/backgrounds stay first-class.

## Hybrid code shape
- Regeneratable: test flow + examples/data.
- Engineering adds write-once tier files (AI writes real production-calling code).
- Layout from story-class shape; regen/step-key discipline from spec+tier.

## Rules / scanners
- Rule prose tightened into `stories.md`; scanners under `context_tools/stories/scanners/` on shared `Scanner` base, operating on the canonical model.
- Cross-language: channels (py/ts/js/java/md/json/…) fill model fields; scanners never branch on file extension. Proven by `scanners/multi_language_scanners_spec.py`.

## Scope
- Port story-specific pieces; leave assembler/`src/skill` behind.
- Leave `abd-skills/stories` in place (do not delete).

## Stories vs BDD
- Stories = acceptance (e2e / tier-layer); BDD = object tests.
