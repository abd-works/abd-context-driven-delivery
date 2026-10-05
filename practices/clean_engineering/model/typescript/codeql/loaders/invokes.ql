/**
 * @name Practice graph invokes
 * @kind problem
 * @id cdd/practice-graph/invokes
 */

import javascript
import subject_filter
import members

from MethodDefinition caller, MethodCallExpr call, MethodDefinition callee
where
  classOperation(caller) and
  classOperation(callee) and
  call.getEnclosingFunction() = caller.getBody() and
  callee.getName() = call.getMethodName()
select caller.getDeclaringType().getName(), caller.getName(),
  callee.getDeclaringType().getName(), callee.getName(),
  caller.getFile().getRelativePath()
