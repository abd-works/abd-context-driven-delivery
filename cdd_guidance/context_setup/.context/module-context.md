# cdd_guidance/context_setup
*Context Setup* captures a project's existing knowledge — a folder of documents, or a live application — and turns it into context the practices can work from: documents are converted to markdown, partitioned through the selected practices (Stories, DDD, UX, Clean Engineering), and embedded into one searchable index. `context-setup.capture_from_documents` runs that whole pipeline for a folder; `context-setup.capture_from_live_app` captures a running web, desktop, or API application through `context-setup.smoke_test`, `context-setup.scout_app`, and `context-setup.complete_capture`; `context-setup.convert` converts a folder of documents to markdown on its own.

*LiveAppCapture* is one capture of a running application, made for the tool call that asks for it: the repository the app runs from, where its stubs and pages are written (the capture repository, or the app's own repository when none is named), its surface, its base URL, and the paths it visits. The three live-app tools take those values as parameters and hand them to a new *LiveAppCapture*, so one call's capture never reaches another's. A page the browser cannot load comes back in `failed_pages` with the browser's reason, so the review step captures it again.

*Context Index* is the searchable index of those segments: `context-index.embed` embeds segment files into a FAISS index, `context-index.search` returns the chunks most relevant to a query, and `context-index.ask` answers a question from the index with citations. *EmbeddingProvider* is the interface an embedding service implements to be used by the index; OpenAI embeddings are the default.

- **Purpose:** Turn existing documents or a running application into partitioned, indexed context that later stages can search and cite.
- **Seam (terms):** ContextSetup, LiveAppCapture, ContextIndex, EmbeddingProvider, `context-setup.capture_from_documents`, `context-setup.capture_from_live_app`, `context-setup.convert`, `context-setup.smoke_test`, `context-setup.scout_app`, `context-setup.complete_capture`, `context-index.embed`, `context-index.search`, `context-index.ask`
- **Dependencies (one-way):** `cdd_guidance/actions/partition` (*Partition*, which partitions through the practices the user selects), `harness/agent_tools`, `harness/installation`, `harness/mcp`; FAISS and an embedding service (OpenAI by default)

## Constraint

Partition through the practices before embedding; the index holds practice segments, not raw documents. Ask and search against an index built by `context-index.embed`, passing its folder as `index_path`. Context Setup is a plain toolset of pipeline steps, not a practice: it has no fidelities to generate or validate (decision `.context/cdr/0001-plain-toolset-not-context-domain.md`).
