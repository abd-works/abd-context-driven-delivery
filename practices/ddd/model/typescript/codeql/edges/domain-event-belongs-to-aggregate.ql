/**
 * @name domain-event-belongs-to-aggregate
 * @kind problem
 * @id cdd/ddd/edges/domain-event-belongs-to-aggregate
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "DomainEvent", parent, _, _, _, _) and
  mod = moduleName(cls) and
  child = aggregateId(mod)
select parent, child, "belongsTo", 4, "relationship"
