/**
 * @name operations
 * @kind problem
 * @id cdd/ce/nodes/operations
 */

import javascript
import ce
import source_span

from MethodDefinition method
where classOperation(method)
select operationId(method), method.getName(), "Operation", "clean_engineering",
  slash(method.getFile().getRelativePath()), sourceStart(method), method.getLocation().getEndLine(),
  method.getDeclaringType().getName()
