# artifacts-live-under-context-root-not-session-subfolder

- **entry_id:** 7a5e9304
- **artifact:** pml-my/.context/story-map.md and .context/sessions/pml-my-current-state/scenarios/
- **rule:** (process) artifacts-live-under-context-root-not-session-subfolder
- **wrong:** Wrote the generated story-map.md, and created a new scenarios/ folder tree, under .context/sessions/pml-my-current-state/ (the ephemeral session-tracking folder: session.md, grill-answers, handoff, mistakes.log) instead of directly under .context/ (the durable artifact root, per session_guidance layout: 'path -> docs -> {path}/.context/; folder -> session.md, grill-answers, engagement sketches, handoff, mistakes.log'). Also started inventing a new parallel scenarios/ subfolder taxonomy instead of mirroring the existing tests/ epic-slug/story-slug folder structure directly under .context/. Same class of mistake as prior entry 0c41f32b (no-nested-context-inside-session).
- **status:** fixed