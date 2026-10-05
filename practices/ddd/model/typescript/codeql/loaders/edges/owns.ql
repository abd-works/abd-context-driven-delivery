/**
 * @name ddd owns
 * @kind problem
 * @id cdd/ddd/owns
 */

import javascript
import ddd

from string parent, string child
where
  parent = dddPracticeId() and child = boundedContextId()
  or
  exists(string mod |
    parent = boundedContextId() and
    aggregateFolder(mod) and
    child = aggregateId(mod)
  )
  or
  exists(ClassDefinition cls, string kind, string mod |
    dddClass(cls, kind, child, _, _, _, _) and
    kind != "EntityRoot" and
    mod = moduleName(cls) and
    parent = aggregateId(mod)
  )
select parent, child, "owns", 2, "direct"
