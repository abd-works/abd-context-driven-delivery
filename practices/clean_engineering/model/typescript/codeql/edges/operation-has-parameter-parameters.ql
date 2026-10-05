/**
 * @name operation-has-parameter-parameters
 * @kind problem
 * @id cdd/ce/edges/operation-has-parameter-parameters
 */

import javascript
import ce

from string parent, string child
where
  exists(MethodDefinition method, Parameter param |
    classOperation(method) and
    method.getName() != "constructor" and
    param = method.getBody().getAParameter() and
    param.getName() != "this" and
    parent = operationId(method) and
    child = parameterId(method, param)
  )
  or
  exists(Function func, Parameter param |
    bareFunction(func) and
    param = func.getAParameter() and
    param.getName() != "this" and
    parent = bareFunctionId(func) and
    child = bareParameterId(func, param)
  )
select parent, child, "hasParameter", 5, "relationship"
