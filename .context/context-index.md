# Context index

Workspace-relative roots for each context tool. Prefer these over defaults when generating. Handoffs must cite this file.

## Current

- bdd = ./utilities/workspace/*
- clean_engineering = ./utilities/workspace/*
- stories = ./*

## Log

- 2026-08-01: stories = ./tests/*
- 2026-08-03: stories = ./utilities/repair/* (was ./tests/*) - repair-evals-loop story-map sketch session
- 2026-08-04: stories = ./../story-ui/* (was ./utilities/repair/*) - Source sketch and story-ui target artifacts for story_map generation
- 2026-08-04: clean_engineering = ./../story-ui/* - Modules-fidelity generation context rooted at story-ui sketch and artifacts
- 2026-08-20: bdd = ./context_tools/* - action-owns-context-tools iterate
- 2026-08-21: clean_engineering = ./context_tools/actions/eval/* (was ./../story-ui/*)
- 2026-08-22: bdd = ./context_tools/actions/workspace/* (was ./context_tools/*)
- 2026-08-26: bdd = ./context_tools/actions/workspace/*; clean_engineering = ./context_tools/actions/workspace/* (eval package deleted)
- 2026-08-26: clean_engineering = ./utilities/git/* (was ./context_tools/actions/workspace/*)
- 2026-08-26: clean_engineering = ./primitives/harness/* (was ./utilities/git/*)
- 2026-08-26: bdd = ./primitives/harness/* (was ./context_tools/actions/workspace/*)
- 2026-08-26: bdd = ./* (was ./primitives/harness/*)
- 2026-08-26: bdd = ./primitives/harness/* (was ./*)
- 2026-08-27: bdd = ./utilities/workspace/* (was ./primitives/harness/*)
- 2026-08-27: clean_engineering = ./utilities/workspace/* (was ./primitives/harness/*)
- 2026-08-28: stories = ./* (was ./../story-ui/*)
- 2026-08-28: clean_engineering = ./* (was ./primitives/harness/*)
- 2026-08-30: bdd = ./utilities/workspace/* (was ./primitives/harness/*)
- 2026-08-30: clean_engineering = ./utilities/workspace/* (was ./*)
