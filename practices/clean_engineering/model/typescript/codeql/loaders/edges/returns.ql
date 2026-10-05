/**
 * @name returns
 * @kind problem
 * @id cdd/ce/edges/returns
 */

import javascript
import ce

from MethodDefinition method, ClassDefinition cls
where
  classOperation(method) and
  domainClass(cls) and
  exists(method.getReturnTypeAnnotation()) and
  hintNames(method.getReturnTypeAnnotation().toString(), cls.getName())
select operationId(method), classId(cls), "returns", 7, "relationship"
