/**
 * @name invokes
 * @kind problem
 * @id cdd/ce/edges/invokes
 */

import javascript
import ce

from MethodDefinition caller, MethodCallExpr call, MethodDefinition callee
where
  classOperation(caller) and
  classOperation(callee) and
  call.getEnclosingFunction() = caller.getBody() and
  callee.getName() = call.getMethodName() and
  mentionsClass(caller.getDeclaringType(), callee.getDeclaringType())
select operationId(caller), operationId(callee), "invokes", 8, "relationship"
