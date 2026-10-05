---
alwaysApply: false
globs:
  - "src/**/*.ts"
---

- **`codeql-loaders-only`** - Populate fills CodeQLKnowledgeGraph only from CodeQL loader queries under `queries/` (CodeQL CLI via `src/codeql.ts`). Source under `src/` does not import `harness/knowledge_graph`, legacy loaders, or a TypeScript AST stand-in (`typescript`, `typescript-source`).
