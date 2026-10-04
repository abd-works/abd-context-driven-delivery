/**
 * @name Practice graph operations
 * @kind problem
 * @id cdd/practice-graph/operations
 */

import javascript
import subject_filter
import source_span
import members

from MethodDefinition method
where classOperation(method)
select method.getDeclaringType().getName(), method.getName(), "",
  sourceStart(method),
  method.getFile().getRelativePath(),
  method.getLocation().getEndLine()
