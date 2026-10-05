/**
 * @name class-depends-on-classes
 * @kind problem
 * @id cdd/ce/edges/class-depends-on-classes
 */

import javascript
import ce

from MethodDefinition caller, MethodCallExpr call, MethodDefinition callee
where
  classOperation(caller) and
  classOperation(callee) and
  call.getEnclosingFunction() = caller.getBody() and
  callee.getName() = call.getMethodName() and
  caller.getDeclaringType() != callee.getDeclaringType() and
  mentionsClass(caller.getDeclaringType(), callee.getDeclaringType())
select classId(caller.getDeclaringType()), classId(callee.getDeclaringType()), "dependsOn", 9,
  "relationship"
