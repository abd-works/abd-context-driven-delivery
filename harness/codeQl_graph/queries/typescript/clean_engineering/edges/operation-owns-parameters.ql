/**
 * @name operation-owns-parameters
 * @kind problem
 * @id cdd/ce/edges/operation-owns-parameters
 */

import javascript
import clean_engineering.ce

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
select parent, child, "owns", 2, "direct" order by parent, child
