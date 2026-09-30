/**
 * @name Practice graph parameters
 * @kind problem
 * @id cdd/practice-graph/parameters-javascript
 */

import javascript

from MethodDefinition method, int index
where
  exists(method.getDeclaringType().getName()) and
  exists(method.getName()) and
  index >= 0 and
  index < method.getNumParameter() and
  exists(method.getParameter(index).getName())
select method.getDeclaringType().getName(), method.getName(), method.getParameter(index).getName(),
  method.getParameter(index).getLocation().getStartLine(),
  method.getFile().getRelativePath(),
  method.getParameter(index).getLocation().getEndLine()
