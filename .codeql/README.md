# CodeQL — practice graph populate

The knowledge graph loader uses **two passes** on the same `PracticeGraph.load(path)` path:

1. **Prose / structure** — story-map, scenarios, domain-model markdown, bounded-context map, BDD descriptions.
2. **CodeQL populate** — when `.codeql/results/practice-graph.json` exists under the workspace (or `codeql_results=` is passed explicitly), merge code facts into the graph.

Markdown tells you *what the stories say*. CodeQL tells you *what the code actually calls, reads, and exports*.

## Output location

```
<workspace>/
  .codeql/
    results/
      practice-graph.json    ← consumed by populate_from_codeql
    logs/
    *-db/                    ← extracted CodeQL database (gitignored)
```

## Export schema (version 1)

See `practices/knowledge_graph/model/codeql_export.py` for dataclasses. Summary:

| Section | Graph edges wired |
|---------|-------------------|
| `classes`, `properties`, `operations` | CE tree (`owns`, `hasType`, `returns`) — creates missing nodes |
| `calls` | `Operation — invokes — Operation` |
| `story_calls` | `Step — invokes — Operation` (join on story file + line) |
| `story_observations` | `Step — observes — Property/Operation` |
| `example_exports` | `Example — demonstrates — Class` |

## Workflow (pml-domainmodel / TypeScript)

```bash
# 1. Create database from the repo root (TypeScript/JavaScript)
codeql database create .codeql/pml-domainmodel-db \
  --language=javascript-typescript \
  --source-root=.

# 2. Run practice-graph queries (to be added under .codeql/queries/)
#    Export SARIF/CSV/BQRS → practice-graph.json

# 3. Load the unified graph
python -c "
from practices.knowledge_graph.model import PracticeGraph
g = PracticeGraph.load('/path/to/pml-domainmodel')
print(len(g.relationships), 'edges')
"
```

## Why CodeQL is required for real codebases

- **Step → Operation** — GWT prose does not name the callee symbol; test bodies do.
- **Operation → Operation** — call graph across files (e.g. `CustomerRepository.load` → `IMavenirClient.fetchCustomer`).
- **Example → Class** — `*.examples.ts` export types must be resolved, not guessed from table labels.
- **Class → Class** — `hasType`, `returns`, and cross-module `dependsOn` from actual TS types, not markdown stubs.

Without CodeQL populate, increment 1 can still load **story hierarchy** from markdown/TS discovery, but cross-practice wiring stays incomplete.

## Fixture

`practices/knowledge_graph/examples/codeql-slice/` — minimal workspace + sample export for specs.
