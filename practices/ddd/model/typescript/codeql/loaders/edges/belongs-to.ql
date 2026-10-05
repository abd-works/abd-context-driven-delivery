/**
 * @name ddd belongs-to
 * @kind problem
 * @id cdd/ddd/belongs-to
 */

import javascript
import ddd

from string parent, string child
where
  exists(string mod |
    child = boundedContextId() and
    aggregateFolder(mod) and
    parent = aggregateId(mod)
  )
  or
  exists(ClassDefinition cls, string kind, string mod |
    dddClass(cls, kind, parent, _, _, _, _) and
    mod = moduleName(cls) and
    child = aggregateId(mod)
  )
select parent, child, "belongsTo", 4, "relationship"
