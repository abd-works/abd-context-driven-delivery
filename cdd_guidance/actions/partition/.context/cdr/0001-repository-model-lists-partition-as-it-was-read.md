# The repository model's Partition entry is corrected when the model is read again, not by a fix agent

**Status:** decided, round 7 (finding L7 of `round7-actions-patterns.md`).

## Decision

`Partition.partition_corpus` was deleted in round 5; no code, spec, recipe, or card in this module names it. The two places that still list it are `.context/repo-model.md:2737` and the Partition box in `.context/repo-model.drawio`. Both are the repository's model as the review lead reads it from the code, and fix agents are told not to edit either. They are corrected the next time the lead reads the model from the code, which lists Partition's members as they are then: `verify_segment_completeness`, `partition_guidance`, `index`, `segment`, `segment_files`, and `partition`.

## Why

- The model is one reading of the whole repository, made at one commit for the reviewers to compare against. A fix agent editing a single entry would make the model show a mix of two commits, so a reviewer could no longer tell which code a line describes.
- The stale entry misleads no one working in this module: the module's own card (`.context/module-context.md`) and `partition.md` name the members as they are, and those are what an agent reads before changing Partition.

## Consequences

The finding leaves the count as decided. When the lead reads the model again, `partition_corpus` drops out and `segment_files` comes in; no further change is needed here.
