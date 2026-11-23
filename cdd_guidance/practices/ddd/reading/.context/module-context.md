# cdd_guidance/practices/ddd/reading
*DddReading* is how DDD takes part in the knowledge graph: after Clean Engineering has read the code, it reads the bounded-context map and domain model documents into bounded context, aggregate, and building block nodes, and links each building block to the Clean Engineering class it describes. It is the practice's `reading_type`, a *PracticeReading* of harness/graph.

- **Purpose:** Keep the graph reading out of DDD's model package, so the model and its formats import nothing that imports them back: the reading imports the markdown format, which imports the model, one way.
- **Seam (terms):** DddReading
- **Dependencies (one-way):** `cdd_guidance/practices/ddd` (its `model` package and the markdown format inside it, the map the reading parses documents into, and its rules), `cdd_guidance/practices/clean_engineering` (*CleanEngineering*, read first, and its `reading` package's facts), `cdd_guidance/practices/source_code` (*HoldsProjectTestCode*, which tells test code from production code), `harness/graph` (*PracticeReading*, nodes, and edges), `harness/markdown` (*MarkdownText*), `harness/annotations` (*Name*), `harness/agent_tools` (progress).

The DDD practice (`ddd.py`) names *DddReading* as its `reading_type`, and this package imports the DDD model, so the two modules form a cycle: neither can change or be tested without the other. Nothing in the DDD `model` package imports this package.

## Constraint

The reading reads facts and links nodes; it writes no document and holds no domain rule. A rule DDD checks lives in the practice's `rules` package and reads the facts recorded here.
