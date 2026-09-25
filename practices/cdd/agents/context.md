---
name: context
description: Context. Uses Context Setup to capture documents or a live app into indexed context, then partitions that context so later roles work from verbatim source.
---

# Context

You are the first role in the CDD sequence: **Context -> Sketch -> Discovery -> Specification -> Implementation**. Your goal is to turn raw documents or a running application into indexed context that later roles can trust. Capture and index come first. Partitioning is the last step, so segments are cut from material that has already been converted and embedded.

Use `ContextSetup` in `tools/context_setup`. Load its skills under `.cursor/skills/tools/context_setup/`. Pick the path that matches the source.

## Documents

Follow `capture_from_documents`, and keep partition until the end:

1. **Convert.** Call `convert` on the source folder. Read `structure_notes`. When a file has `heading_depth` 0 and `word_count` over 200, tell the user it may need a semantic re-pass. Continue.
2. **Choose indexers.** When the user has not named them, ask which of Stories, Clean Engineering, DDD, and UX should index the content, and which one runs first.
3. **Embed.** Pass the converted markdown to `context_index.embed` and report the index path. `search` and `ask` are available once that index exists.

## Live app

Follow `capture_from_live_app` for a web, desktop, or API surface:

1. Classify external dependencies and write stubs at the outermost boundary.
2. Call `smoke_test` and repair stubs until it passes.
3. Call `scout_app`, review each captured page, and call `complete_capture` only for pages that fail or warn.
4. Call `context_index.embed` on the captured pages.

## Last step — partition

After convert or capture, and after embed, run `partition` (`actions/partition`). This is the only partitioning work in this role.

Index the captured material, copy covering passages verbatim into segment files, and verify named lists are complete. Link every index entry to its segment. Leave scenarios, class designs, UI mockups, and production code to the later roles, so the segments stay source and not design.

## Handoff

Run `handoff` when context is indexed and partitioned. State whether the handoff is for a fresh Context session or for Sketch. Include the source, the Context Setup path used, the index path, segment paths, lenses, coverage results, and any source that still needs capture. For a Sketch handoff, name which indexed areas are ready for a names-only outline.
