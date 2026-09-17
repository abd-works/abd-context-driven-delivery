# Context index

Workspace-relative roots for each context tool. Prefer these over defaults when generating. Handoffs must cite this file.

## Current

- bdd = ./primitives/harness/*
- clean_engineering = ./*
- stories = ./*

## Log

- 2026-08-01: stories = ./tests/*
- 2026-08-03: stories = ./utilities/repair/* (was ./tests/*) - repair-evals-loop story-map sketch session
- 2026-08-04: stories = ./../story-ui/* (was ./utilities/repair/*) - Source sketch and story-ui target artifacts for story_map generation
- 2026-08-04: clean_engineering = ./../story-ui/* - Modules-fidelity generation context rooted at story-ui sketch and artifacts
- 2026-08-20: bdd = ./practices/* - action-owns-context-tools iterate
- 2026-08-21: clean_engineering = ./actions/eval/* (was ./../story-ui/*)
- 2026-08-22: bdd = ./actions/workspace/* (was ./practices/*)
- 2026-08-26: bdd = ./actions/workspace/*; clean_engineering = ./actions/workspace/* (eval package deleted)
- 2026-08-26: clean_engineering = ./utilities/git/* (was ./actions/workspace/*)
- 2026-08-26: clean_engineering = ./primitives/harness/* (was ./utilities/git/*)
- 2026-08-26: bdd = ./primitives/harness/* (was ./actions/workspace/*)
- 2026-08-26: bdd = ./* (was ./primitives/harness/*)
- 2026-08-26: bdd = ./primitives/harness/* (was ./*)
- 2026-08-27: bdd = ./utilities/workspace/* (was ./primitives/harness/*)
- 2026-08-27: clean_engineering = ./utilities/workspace/* (was ./primitives/harness/*)
- 2026-08-28: stories = ./* (was ./../story-ui/*)
- 2026-08-28: clean_engineering = ./* (was ./primitives/harness/*)
