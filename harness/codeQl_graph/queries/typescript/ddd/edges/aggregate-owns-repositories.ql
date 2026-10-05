/**
 * @name aggregate-owns-repositories
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-repositories
 */

import javascript
import ddd.ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "Repository", child, _, _, _, _) and
  mod = moduleName(cls) and
  parent = aggregateId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
