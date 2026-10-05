---
alwaysApply: false
globs:
  - "src/**/*.ts"
  - "examples/input/**/*.ts"
---

- **`ddd-graph-stereotypes-only`** - A DDD practice graph holds only DDD stereotypes (BoundedContext, Aggregate, Entity, EntityRoot, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory). Exception, Node, Client, Property, and unstereotyped OoadClass stay off that graph.
- **`codeql-loaders-only`** - The knowledge graph is filled from CodeQL loader queries in `queries/`. Populate does not import `harness/knowledge_graph`, legacy loaders, or a TypeScript AST stand-in for those queries.
