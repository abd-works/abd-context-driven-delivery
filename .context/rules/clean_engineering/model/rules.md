```yaml
alwaysApply: false
globs: "**/knowledge-graph/graph.ts,**/codeql_model.py,**/codeql.py,**/explore-knowledge-graph/**/*.ts"
```

- **`edges-from-loader-queries`** - CodeQL loaders emit every node and every edge; populate only registers nodes then relates each edge; the explorer sorts by `sequential_order` and lists `immediate=true` children under the parent while `immediate=false` children sit under a collapse named after the kind, because stitching relatives, properties, DDD stereotypes, or owns in Python or TypeScript rebuilds structure the loaders already know.
