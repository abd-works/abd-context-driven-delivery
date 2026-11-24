# cdd_guidance/context_setup

*ContextSetup* converts documents to markdown, which Partition calls before it partitions them, and captures a live app through *LiveAppCapture*; *ContextIndex* embeds the segments and answers questions with citations. The cdd server makes each for the call it answers, so the folders a call names are read from that call's session's project.

- **Purpose:** Turn existing documents or a running application into partitioned, indexed context that later stages can search and cite.
- **Seam (terms):** ContextSetup, ContextIndex, EmbeddingProvider
- **Dependencies (one-way):** harness/agent_tools, harness/installation, harness/markdown, harness/mcp, harness/guidance_actions (*ActionWorksInNoSession*)

## ContextSetup

Convert a folder of documents to markdown, and capture a live application into indexed context.

+ ContextSetup(context_index: ContextIndex | None = None, session: Any = None)
------
+ << composition >> context_index: ContextIndex
+ session: Any
	// the session it works in
----
+ for_call(call: ToolCall): ContextSetup
+ in_session(session: Any): ContextSetup
+ convert(folder_path: str): ConversionResult
+ smoke_test(repo_path: str, surface: str = 'web', capture_repo: str = '', base_url: str = '', entry_paths: list[str] | None = None): SmokeTestResult
+ scout_app(repo_path: str, surface: str = 'web', capture_repo: str = '', base_url: str = '', entry_paths: list[str] | None = None): ScoutResult
+ complete_capture(repo_path: str, missing_pages: list[str], surface: str = 'web', capture_repo: str = '', base_url: str = ''): CaptureResult
+ capture_from_live_app(repo_path: str, capture_repo: str = '', surface: str = 'web'): str
---<<creates>>--> ContextIndex
---<<creates>>--> LiveAppCapture
---<<reads session of>>--> ToolCall

## ContextIndex

Embed partitioned segments into a FAISS index and answer questions with source citations.

+ ContextIndex(embedding_provider: EmbeddingProvider = LIVE_EMBEDDINGS, session: Any = None)
------
----
+ for_call(call: ToolCall): ContextIndex
+ in_session(session: Any): ContextIndex
+ embed(segments_paths: list[str], out_path: str): EmbedResult
+ search(query: str, index_path: str, top_k: int = 5): SearchResult
+ ask(question: str, index_path: str): str
---<<embeds with>>--> EmbeddingProvider
---<<creates>>--> SegmentIndex
---<<reads session of>>--> ToolCall

## EmbeddingProvider : Protocol

What turns text into vectors; OpenAI's embedding service by default.

------
----
+ embed_texts(texts: list[str]): list[list[float]]
+ embed_query(text: str): list[float]
