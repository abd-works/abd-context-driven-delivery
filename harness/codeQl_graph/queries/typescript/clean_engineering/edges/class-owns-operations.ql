/**
 * @name class-owns-operations
 * @kind problem
 * @id cdd/ce/edges/class-owns-operations
 */

import javascript
import clean_engineering.ce

from MethodDefinition method, string parent, string child
where
  classOperation(method) and
  parent = classId(method.getDeclaringType()) and
  child = operationId(method)
select parent, child, "owns", 2, "direct" order by parent, child
