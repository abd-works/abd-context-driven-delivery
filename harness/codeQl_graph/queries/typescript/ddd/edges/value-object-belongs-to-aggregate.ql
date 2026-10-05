/**
 * @name value-object-belongs-to-aggregate
 * @kind problem
 * @id cdd/ddd/edges/value-object-belongs-to-aggregate
 */

import javascript
import ddd.ddd

from ClassDefinition cls, string parent, string child, string mod
where
  dddClass(cls, "ValueObject", parent, _, _, _, _) and
  mod = moduleName(cls) and
  child = aggregateId(mod)
select parent, child, "belongsTo", 4, "relationship"
