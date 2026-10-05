/**
 * @name repository-belongs-to-aggregate
 * @kind problem
 * @id cdd/ddd/edges/repository-belongs-to-aggregate
 */

import javascript
import ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "Repository", parent, _, _, _, _) and
  mod = moduleName(cls) and
  child = aggregateId(mod)
select parent, child, "belongsTo", 4, "relationship"
