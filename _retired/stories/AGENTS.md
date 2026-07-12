# Stories Workspace — Agent Rules

## Folder hierarchy

Story map hierarchy maps directly to folders on disk. Every test and scenario file must follow:

```
{epic-slug}/
  {sub-epic-slug}/
    {lowest-sub-epic-slug}/
      {lowest-sub-epic-slug}-stories.ts     ← scenario data (spec)
      {lowest-sub-epic-slug}-domain.test.ts ← tier file (AI fills bodies)
      {lowest-sub-epic-slug}-server.test.ts
      {lowest-sub-epic-slug}-e2e.test.ts
```

Never write flat. File named after **lowest-sub-epic**, not the story.

## Scaffolding vs AI — who writes what

| File | Producer | Rule |
|---|---|---|
| `{lowest-sub-epic}-stories.ts` | Code path (first render); AI (small in-place edits only) | Must stay round-trippable |
| `{lowest-sub-epic}-{layer}.test.ts` | Code path scaffolds once (empty bodies); **AI fills bodies** | Write-once skeleton; AI owns bodies from first emit |
| `story-types.ts` | Code path only | **AI never edits this file** |
| `story-runner.ts` | Code path only | **AI never edits this file** |
| `story-context.md` (any level) | AI / human | Prose only; code path never writes here |

To scaffold new stories or re-render structure run:
```bash
python stories/cli/main.py create --workspace <path> --format ts --tiers domain,server,e2e
```

## Paths

All file paths in generated or edited content must be **absolute from the workspace root** to remain valid when folder structure changes.

## Skills

Reference skills by **name**, not by path — skills move between deployments.
