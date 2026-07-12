---
generated-using: "@capability/{capability}/{capability}.md"
extends: extend
overrides: [create, is-a-valid]
open: [identify, discover]
---

Define, discover, and deploy CDD capabilities.

## Create

Create or update capability {capability}. For a new capability, generate the full folder from the template. For an existing capability, add new `## Action` sections for {actions} to the agentic surface and corresponding methods to the API surface following the same template pattern.

read in full → `{capability}/{capability}.md`

## Identify

Check whether {path} is a valid CDD capability.

```
python -m capability identify <path>
```

## Discover

Find all CDD capabilities under {root}.

```
python -m capability discover <root> [--recursive]
```

## Is Valid

Check whether {capability} was generated from the capability template.

read in full → `{capability}/{capability}.md`

Search {capability} for files that conform to each item in the template and verify each checklist item:

- [ ] folder contains `{capability}.md` and `{capability}.py`
- [ ] each `{capability}.{ext}` file carries `generated-using: @capability/{capability}/{capability}.{ext}` front matter
- [ ] `{capability}.md` has a one-sentence description, at least one `##` action, and `## Is A Valid`
- [ ] every `##` action that generates output is named `## Create`
- [ ] all `{placeholders}` have been replaced with real values
- [ ] if a template was built for the output artifact, it exists at `{capability}/{capability}.md`
- [ ] if references were extracted, each one exists at `references/{concept}.md` and is linked with `read in full →`
