/**
 * @name aggregate-owns-specifications
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-specifications
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "Specification", child, _, _, _, _) and
  mod = moduleName(cls) and
  parent = aggregateId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
