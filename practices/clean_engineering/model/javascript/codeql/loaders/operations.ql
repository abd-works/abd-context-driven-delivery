/**
 * @name Practice graph operations
 * @kind problem
 * @id cdd/practice-graph/operations
 */

import javascript
import subject_filter
import source_span

from MethodDefinition method
where inSubject(method) and exists(method.getDeclaringType().getName())
select method.getDeclaringType().getName(), method.getName(), "",
  sourceStart(method),
  method.getFile().getRelativePath(),
  method.getLocation().getEndLine()
