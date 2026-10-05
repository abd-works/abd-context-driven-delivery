/**
 * @name specification-belongs-to-aggregate
 * @kind problem
 * @id cdd/ddd/edges/specification-belongs-to-aggregate
 */

import javascript
import ddd.ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "Specification", parent, _, _, _, _) and
  mod = moduleName(cls) and
  child = aggregateId(mod)
select parent, child, "belongsTo", 4, "relationship"
