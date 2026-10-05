/**
 * @name aggregate-owns-domain-events
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-domain-events
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "DomainEvent", child, _, _, _, _) and
  mod = moduleName(cls) and
  parent = aggregateId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
