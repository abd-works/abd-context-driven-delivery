/**
 * @name aggregate-owns-value-objects
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-value-objects
 */

import javascript
import ddd.ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "ValueObject", child, _, _, _, _) and
  mod = moduleName(cls) and
  parent = aggregateId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
