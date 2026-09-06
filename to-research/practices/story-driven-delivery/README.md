# Story-driven delivery

Story map → acceptance criteria → specification → acceptance tests.

**Practice skills:** abd-story-mapping, abd-thin-slicing, abd-story-acceptance-criteria, abd-story-specification, abd-story-acceptance-test

**Shared reference:** [`reference/`](reference/stories-perspective.md) — perspective ladder, incomplete context, new vs existing system, diagram workflow, domain input priority, validate checklist.

**Per skill:** `reference/` (all files, including `generate.md` when present), `templates/` (all files). Workflow: [`common/reference/skill-workflow.md`](../../common/reference/skill-workflow.md). Validation: `rules/` + scanners — no `## Validate` in `SKILL.md`.

## Deploy

```powershell
& scripts/deploy-skills.ps1 -Force
```
