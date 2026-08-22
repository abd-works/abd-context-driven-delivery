# Context index

Workspace-relative roots for each context tool. Prefer these over defaults when generating. Handoffs must cite this file.

## Current

- bdd = ./context_tools/actions/eval/*
- clean_engineering = ./context_tools/actions/eval/*
- stories = ./../story-ui/*

## Log

- 2026-08-01: stories = ./tests/*
- 2026-08-03: stories = ./utilities/repair/* (was ./tests/*) - repair-evals-loop story-map sketch session
- 2026-08-04: stories = ./../story-ui/* (was ./utilities/repair/*) - Source sketch and story-ui target artifacts for story_map generation
- 2026-08-04: clean_engineering = ./../story-ui/* - Modules-fidelity generation context rooted at story-ui sketch and artifacts
- 2026-08-20: bdd = ./context_tools/* - action-owns-context-tools iterate
- 2026-08-21: clean_engineering = ./context_tools/actions/eval/* (was ./../story-ui/*)
- 2026-08-22: bdd = ./context_tools/actions/workspace/* (was ./context_tools/*)
- 2026-08-22: bdd = ./context_tools/actions/eval/* (was ./context_tools/actions/workspace/*)
