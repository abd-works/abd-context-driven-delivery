/**
 * @name aggregate-owns-domain-services
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-domain-services
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "DomainService", child, _, _, _, _) and
  mod = moduleName(cls) and
  parent = aggregateId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
