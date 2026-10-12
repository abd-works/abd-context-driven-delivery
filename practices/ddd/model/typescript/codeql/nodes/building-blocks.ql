/**
 * @name ddd building blocks
 * @kind problem
 * @id cdd/ddd/building-blocks
 */

import javascript
import ddd

predicate block(
  string id, string name, string kind, string file, int start, int end, string stage
) {
  exists(string classKind |
    dddClass(_, classKind, id, name, file, start, end) and
    kind = classKind and
    stage = "implementation"
  )
  or
  exists(string mod |
    aggregateFolder(mod) and
    file = aggregateRoot(mod) and
    id = aggregateId(mod) and
    name = mod.regexpCapture(".*/([^/]+)$", 1) and
    kind = "Aggregate" and
    start = 1 and
    end = 1 and
    stage = "specification"
  )
  or
  implicitContext() and
  id = dddNodeId("BoundedContext", ".", "bounded context") and
  name = "bounded context" and
  file = "." and
  kind = "BoundedContext" and
  start = 1 and
  end = 1 and
  stage = "discovery"
  or
  exists(string dir, string contextName |
    contextPath(dir, contextName) and
    id = dddNodeId("BoundedContext", dir, contextName) and
    name = contextName and
    file = dir and
    kind = "BoundedContext" and
    start = 1 and
    end = 1 and
    stage = "discovery"
  )
}

from string id, string name, string kind, string file, int start, int end, string stage
where block(id, name, kind, file, start, end, stage)
select id, name, kind, "ddd", file, start, end, stage
