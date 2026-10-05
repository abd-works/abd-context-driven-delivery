/**
 * @name operation-returns-class
 * @kind problem
 * @id cdd/ce/edges/operation-returns-class
 */

import javascript
import clean_engineering.ce

from MethodDefinition method, ClassDefinition cls
where
  classOperation(method) and
  domainClass(cls) and
  exists(method.getBody().getReturnTypeAnnotation()) and
  hintNames(method.getBody().getReturnTypeAnnotation().toString(), cls.getName())
select operationId(method), classId(cls), "returns", 7, "relationship"
