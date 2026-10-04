/**
 * @name Practice graph parameters
 * @kind problem
 * @id cdd/practice-graph/parameters
 */

import javascript
import subject_filter
import members

from MethodDefinition method, Parameter param
where
  classOperation(method) and
  method.getName() != "constructor" and
  param = method.getBody().getAParameter() and
  param.getName() != "this"
select method.getDeclaringType().getName(), method.getName(), param.getName(),
  param.getLocation().getStartLine(),
  param.getFile().getRelativePath(),
  param.getLocation().getEndLine()
