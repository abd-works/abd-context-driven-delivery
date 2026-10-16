```yaml
alwaysApply: false
globs: "**/harness/graph/**/*.py,**/harness/graph/**/*.ts,**/explore-knowledge-graph/**/*.ts"
```

- **`edges-from-loader-queries`** - The working-copy loader emits every node and every edge; populate only registers nodes then relates each edge; the explorer sorts by `sequential_order` and lists `immediate=true` children under the parent while `immediate=false` children sit under a collapse named after the kind, because stitching relatives, properties, DDD stereotypes, or owns in the UI rebuilds structure the loader already registered.
