# Context index

Workspace-relative roots for each context tool. Prefer these over defaults when generating. Handoffs must cite this file.

## Current

- bdd = ./primitives/installer/*
- clean_engineering = ./*
- stories = ./*

## Log

- 2026-08-01: stories = ./tests/*
- 2026-08-03: stories = ./tools/repair/* (was ./tests/*) - repair-evals-loop story-map sketch session
- 2026-08-04: stories = ./../story-ui/* (was ./tools/repair/*) - Source sketch and story-ui target artifacts for story_map generation
- 2026-08-04: clean_engineering = ./../story-ui/* - Modules-fidelity generation context rooted at story-ui sketch and artifacts
- 2026-08-20: bdd = ./practices/* - action-owns-context-tools iterate
- 2026-08-21: clean_engineering = ./actions/eval/* (was ./../story-ui/*)
- 2026-08-22: bdd = ./actions/workspace/* (was ./practices/*)
- 2026-08-26: bdd = ./actions/workspace/*; clean_engineering = ./actions/workspace/* (eval package deleted)
- 2026-08-26: clean_engineering = ./tools/git/* (was ./actions/workspace/*)
- 2026-08-26: clean_engineering = ./primitives/installer/* (was ./tools/git/*)
- 2026-08-26: bdd = ./primitives/installer/* (was ./actions/workspace/*)
- 2026-08-26: bdd = ./* (was ./primitives/installer/*)
- 2026-08-26: bdd = ./primitives/installer/* (was ./*)
- 2026-08-27: bdd = ./tools/workspace/* (was ./primitives/installer/*)
- 2026-08-27: clean_engineering = ./tools/workspace/* (was ./primitives/installer/*)
- 2026-08-28: stories = ./* (was ./../story-ui/*)
- 2026-08-28: clean_engineering = ./* (was ./primitives/installer/*)
