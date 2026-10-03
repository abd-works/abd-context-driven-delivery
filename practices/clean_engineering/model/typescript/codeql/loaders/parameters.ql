/**
 * @name Practice graph parameters
 * @kind problem
 * @id cdd/practice-graph/parameters
 */

import javascript
import subject_filter

from MethodDefinition method, Parameter param
where
  inSubject(method) and
  exists(method.getDeclaringType().getName()) and
  param = method.getBody().getAParameter() and
  param.getName() != "this"
select method.getDeclaringType().getName(), method.getName(), param.getName(),
  param.getLocation().getStartLine(),
  param.getFile().getRelativePath(),
  param.getLocation().getEndLine()
