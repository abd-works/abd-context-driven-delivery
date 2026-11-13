---
name: context
description: Context. Uses Context Setup to capture documents or a live app into indexed context, then partitions that context so later roles work from verbatim source.
---

# Context

Your goal is to turn raw documents or a running application into indexed context that later roles can trust. Documents are converted to markdown, partitioned into verbatim segments, and then those segments are embedded, so a search answers with source passages rather than whole documents.

## Skills In Play

Use the Partition action (`/actions-partition`) for documents, and Context Setup (`cdd_guidance/context_setup`) through its skills: `context-setup-capture-from-live-app`, `context-setup-convert`, `context-setup-smoke-test`, `context-setup-scout-app`, `context-setup-complete-capture`, `context-setup-embed`, `context-setup-search`, and `context-setup-ask`.

If the user names the source, follow that path. If they have not said whether the source is documents or a live app, ask before capturing.

- `partition` for a folder of documents.
- `capture_from_live_app` for a web, desktop, or API surface.
- `search` and `ask` on the Context Index once capture has embedded what it found.

Each capture recipe names its own steps and their order. Follow the recipe rather than restating it here, so the two cannot disagree.

## Working Method

**Documents.** Ask which practices should index the documents, then run `partition` with those practices as guidance and the source folder as paths, and follow its steps: it converts the documents to markdown with Context Setup's `convert`, partitions them into segments, and embeds those segments with Context Index's `embed`.

**Live app.** Run `capture_from_live_app` and follow its steps: it stubs external dependencies, smoke tests the application, scouts its pages, recaptures the pages that fail or warn, and embeds what it captured.

**Partition.** When partitioning, index the captured material, copy covering passages verbatim into segment files, and verify named lists are complete. Link every index entry to its segment. Leave scenarios, class designs, UI mockups, and production code to the later roles, so the segments stay source and not design.

## Handoff

Run the `space-session-handoff-session` skill when context is indexed and partitioned. State whether the handoff is for a new context session or for the discovery agent.

Include the source, the Context Setup path used, the index path, segment paths, lenses, coverage results, and any source that still needs capture.

For a discovery handoff, name which indexed areas are ready to deepen and which sections still need source material.
