# cdd_guidance/practices/ddd/reading
*DddReading* is how DDD takes part in the knowledge graph: after Clean Engineering has read the code, it reads the bounded-context map and domain model documents into bounded context, aggregate, and building block nodes, and links each building block to the Clean Engineering class it describes. It is the practice's `reading_type`, a *PracticeReading* of harness/graph.

- **Purpose:** Keep the graph reading out of DDD's model package, so the model and its formats import nothing that imports them back: the reading imports the markdown format, which imports the model, one way.
- **Seam (terms):** DddReading
- **Dependencies (one-way):** `cdd_guidance/practices/ddd/model` and `model/markdown` (the map the reading parses documents into), `cdd_guidance/practices/clean_engineering` (*CleanEngineering*, read first, and its `reading` package's facts), `harness/graph` (*PracticeReading*, nodes, and edges). Nothing in `ddd/model` imports this package; `ddd.py` names *DddReading* as its `reading_type`.

## Constraint

The reading reads facts and links nodes; it writes no document and holds no domain rule. A rule DDD checks lives in the practice's `rules` package and reads the facts recorded here.
