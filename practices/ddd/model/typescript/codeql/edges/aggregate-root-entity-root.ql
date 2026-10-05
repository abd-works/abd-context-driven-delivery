/**
 * @name aggregate-root-entity-root
 * @kind problem
 * @id cdd/ddd/edges/aggregate-root-entity-root
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "EntityRoot", child, _, _, _, _) and
  mod = moduleName(cls) and
  parent = aggregateId(mod)
select parent, child, "root", 1, "direct" order by parent, child
