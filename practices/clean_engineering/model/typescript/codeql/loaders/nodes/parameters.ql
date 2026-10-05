/**
 * @name parameters
 * @kind problem
 * @id cdd/ce/nodes/parameters
 */

import javascript
import ce

from MethodDefinition method, Parameter param
where
  classOperation(method) and
  method.getName() != "constructor" and
  param = method.getBody().getAParameter() and
  param.getName() != "this"
select parameterId(method, param), param.getName(), "Parameter", "clean_engineering",
  slash(param.getFile().getRelativePath()), param.getLocation().getStartLine(),
  param.getLocation().getEndLine(), method.getDeclaringType().getName(), method.getName()
