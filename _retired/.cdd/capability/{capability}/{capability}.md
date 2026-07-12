<!--
HOW TO USE THIS TEMPLATE
========================
1. Copy this folder to {capability}/
2. Rename {capability} everywhere: folder name, {capability}.md, {capability}.py
3. Add front matter to all files created, pointing back to this template:
     {capability}.md → ---
                        generated-using: "@capability/{capability}/{capability}.md"
                        extends: capability
                        overrides: [create, is-a-valid]
                        ---
     {capability}.py → # generated-using: @capability/{capability}/{capability}.py
4. Fill in all {placeholders}
5. Add one ## section per action the capability performs
6. To inherit deploy/clean/open/extend, extend `capability` (implements `extend`) — set `extends:` / `overrides:` in frontmatter; do not use @injected
7. Mark actions open for extension with `python -m extend open <path> <action> …` — sets `open: [action, …]` in frontmatter
8. Scaffold a new extender with `python -m extend extend <source> <target-path> <action> …` — sets `extends:` and `overrides:`
9. If this capability generates/creates/builds anything, the section MUST be named ## Create
9. Add {parameters} to action signatures where the agent needs input from the user
10. Deterministic vs prose — per action, decide what must be exact and repeatable:
    - Judgment, drafting, review → keep in `{capability}.md` only
    - Parse, validate, copy, deploy, discover → implement in `{Capability}` class; `{Capability}Cli` routes to it
    - Never let the agent create ad-hoc scripts for core capability behavior — promote to `{Capability}` instead
    - Fuller guidance: read in full → `references/deterministic-code.md`
10. For large or distinct concepts that would bloat this file, extract to a references/ file:
    - Create `references/{concept}.md` with the full detail
    - In this file, replace the inline detail with: read in full → `references/{concept}.md`
    - Keep references/ lean — many reference files signal the capability needs splitting (singularity)
    - Fuller guidance: read in full → `references/{reference-name}.md`
11. If the output artifact is complex (multi-file, structured, has its own rules), create a template for it:
    - Create `{capability}/` folder as the output template
    - Add a `HOW TO USE THIS TEMPLATE` comment to the template following this same pattern
    - In the ## Create action body point to it: read in full → `{capability}/{capability}.md`

-->

---
generated-using: "@capability/{capability}/{capability}.md"
extends: capability
overrides: [create, is-a-valid]
---

{One sentence describing what this capability does.}

## {Action 1}

{One sentence describing this action.} Requires {param-one} and {param-two}.

read in full → `{sub-file}.md`

## Create

Create a new {artifact} from the {capability} template.

read in full → `{capability}/{capability}.md`

## Is A Valid

Check whether {artifact} was generated from this capability's template.

read in full → `{capability}/{capability}.md`

Search {artifact} for files that conform to each item in the template and verify each checklist item:

- [ ] folder contains `{artifact}.md` and `{artifact}.py`
- [ ] each `{artifact}.{ext}` file carries `generated-using: @{capability}/{capability}/{capability}.{ext}` front matter
- [ ] every `##` action that generates output is named `## Create`
- [ ] all `{placeholders}` have been replaced with real values
- [ ] if a template was built for the output artifact, it exists at `{artifact}/{artifact}.md`
- [ ] if references were extracted, each one exists at `references/{concept}.md` and is linked with `read in full →`
