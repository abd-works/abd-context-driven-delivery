# Document channel — architecture

**Package:** `contexts/stories/document/`

## Role

Markdown and JSON are **documentation / interchange** channels for the canonical `StoryMap`.

| Direction | Behavior |
|---|---|
| model → markdown | Full templates: story headers, domain terms, evidence, scenarios (GWT), **examples tables**, Example factories lines |
| markdown → model | Parse those sections into `StoryMap` / `Scenario.example_rows` |
| model → code (via code channel) | Runnable `*_story` + helpers as **stubs**; AI fills method bodies |
| code → markdown | Re-emit documentation templates from model fields (domain terms, example_rows, etc.) |

Code does **not** live under `document/`. Executable shape: see `contexts/stories/code/` and CDR `0001-runnable-story-files-over-pure-data`.

## Layout (real files)

```
document/
  markdown/
    nodes.py              # MarkdownStoryMap, MarkdownScenario, thin-slice
    example_factories.py  # Example factories: `TypeExampleFactory`
    tree.py               # story-map.md adapter
  json/
    nodes.py              # JsonStoryMap (+ exampleFactories, domainTerms, exampleRows)
  architecture-context.md # this file
```

## MarkdownScenario

- **Parse:** Scenario / Scenario Outline, Background, Examples tables → `example_rows`.
- **Render:** `MarkdownScenario.render_scenarios(...)` emits the same shape for code→md / model→md.

## JSON

Round-trips `exampleFactories` on epics/sub-epics, `domainTerms` / `evidence` on stories, `exampleRows` on scenarios.
