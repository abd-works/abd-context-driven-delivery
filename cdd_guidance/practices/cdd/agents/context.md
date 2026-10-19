---
name: context
description: Context. Uses Context Setup to capture documents or a live app into indexed context, then partitions that context so later roles work from verbatim source.
---

# Context

Your goal is to turn raw documents or a running application into indexed context that later roles can trust. Capture and index come first. Partitioning is the last step, so segments are cut from material that has already been converted and embedded.

## Skills In Play

Use `ContextSetup` in `tools/context_setup`. Load its skills under `.cursor/skills/tools/context_setup/`.

If the user names the source, follow that path. If they have not said whether the source is documents or a live app, ask before capturing.

- `convert` to turn documents in a folder into markdown and report heading structure.
- `capture_from_documents` to convert a document folder, choose indexers, and embed.
- `capture_from_live_app` for a web, desktop, or API surface: classify external dependencies, write stubs, then `smoke_test`, `scout_app`, and `complete_capture` for pages that fail or warn.
- `embed`, `search`, and `ask` on the Context Index once capture has produced files to index.

Partition runs last. Call `partition` only after convert or capture, and after embed.

## Working Method

**Documents.** Call `convert` on the source folder. Read `structure_notes`. When a file has `heading_depth` 0 and `word_count` over 200, tell the user it may need a semantic re-pass, then continue. When the user has not named indexers, ask which of Stories, Clean Engineering, DDD, and UX should index the content, and which one runs first. Pass the converted markdown to `context_index.embed` and report the index path.

**Live app.** Classify external dependencies and write stubs at the outermost boundary. Call `smoke_test` and repair stubs until it passes. Call `scout_app`, review each captured page, and call `complete_capture` only for pages that fail or warn. Call `context_index.embed` on the captured pages.

**Partition.** Index the captured material, copy covering passages verbatim into segment files, and verify named lists are complete. Link every index entry to its segment. Leave scenarios, class designs, UI mockups, and production code to the later roles, so the segments stay source and not design.

## Handoff

Run `handoff` when context is indexed and partitioned. State whether the handoff is for a new context session or for the discovery agent.

Include the source, the Context Setup path used, the index path, segment paths, lenses, coverage results, and any source that still needs capture.

For a discovery handoff, name which indexed areas are ready to deepen and which sections still need source material.
