# Grill Answers

### Partition vs semantic tagging

Context tools already tag by view through `Partition`: each tool's `.partition()` builds an index and segments through its own lens (Stories → story, CE → modules/arch, DDD → domain, UX → screens). `context_setup` does not invent a parallel tagger for those lenses — it delegates. See `base_context_tool.py` (`self.partitioner = Partition()`, `partition()` forwarding `slug`/`scaffold`) and `utilities/partition/partition.md`.

### How context_setup uses Partition

Compose by instantiating concrete context tools at compile time and calling `.partition()` on each. User names which tools to run and which runs first; AI Chat sequences the rest after reading the first partition output. Option off of capture: "I want a partition" with a tool list + entry point.

### Default when no context tool is selected

Present all options via AskQuestion (Stories, CE, DDD, UX, CDD, plus default Semantic Indexer). The default is the existing conversion-skill semantic indexer (`abd-context-semantic-index` four-view tagging) — not Partition with an empty slug, and not a silent no-op.

### Compile-time tool references

`ContextSetup` holds direct references to the concrete context tool classes — not string paths, not a protocol-only list.

### Toolset count

Two `@toolsets`: `ContextSetup` (orchestration, document conversion, partition delegation) and `ContextIndex` (embed + search / ask). `AppCapture` is a separate toolset when Increment 2 activates.
