/**
 * @name owns
 * @kind problem
 * @id cdd/ce/edges/owns
 */

import javascript
import ce

from string parent, string child
where
  exists(string mod | subjectModule(mod) and parent = practiceId() and child = moduleId(mod))
  or
  exists(ClassDefinition cls |
    domainClass(cls) and
    parent = moduleId(moduleOf(cls)) and
    child = classId(cls)
  )
  or
  exists(MethodDefinition method |
    classOperation(method) and
    parent = classId(method.getDeclaringType()) and
    child = operationId(method)
  )
  or
  exists(MethodDefinition method, Parameter param |
    classOperation(method) and
    method.getName() != "constructor" and
    param = method.getBody().getAParameter() and
    param.getName() != "this" and
    parent = operationId(method) and
    child = parameterId(method, param)
  )
select parent, child, "owns", 2, "direct" order by parent, child
