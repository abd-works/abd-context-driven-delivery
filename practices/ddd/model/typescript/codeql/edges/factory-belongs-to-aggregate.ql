/**
 * @name factory-belongs-to-aggregate
 * @kind problem
 * @id cdd/ddd/edges/factory-belongs-to-aggregate
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "Factory", parent, _, _, _, _) and
  mod = moduleName(cls) and
  child = aggregateId(mod)
select parent, child, "belongsTo", 4, "relationship"
