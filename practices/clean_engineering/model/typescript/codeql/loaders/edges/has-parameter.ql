/**
 * @name has-parameter
 * @kind problem
 * @id cdd/ce/edges/has-parameter
 */

import javascript
import ce

from MethodDefinition method, Parameter param
where
  classOperation(method) and
  method.getName() != "constructor" and
  param = method.getBody().getAParameter() and
  param.getName() != "this"
select operationId(method), parameterId(method, param), "hasParameter", 5, "relationship"
