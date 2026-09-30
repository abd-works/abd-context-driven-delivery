/**
 * @name Practice graph operations
 * @kind problem
 * @id cdd/practice-graph/operations-javascript
 */

import javascript

string returnedName(MethodDefinition method) { result = "" }

from MethodDefinition method
where exists(method.getDeclaringType().getName()) and exists(method.getName())
select method.getDeclaringType().getName(), method.getName(), returnedName(method),
  method.getLocation().getStartLine(),
  method.getFile().getRelativePath(),
  method.getLocation().getEndLine()
