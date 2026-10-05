/**
 * @name Practice graph depends-on
 * @kind problem
 * @id cdd/practice-graph/depends-on
 */

import javascript
import subject_filter
import members

from MethodDefinition caller, MethodCallExpr call, MethodDefinition callee
where
  classOperation(caller) and
  classOperation(callee) and
  call.getEnclosingFunction() = caller.getBody() and
  callee.getName() = call.getMethodName() and
  caller.getDeclaringType() != callee.getDeclaringType()
select caller.getDeclaringType().getName(), callee.getDeclaringType().getName(),
  caller.getLocation().getStartLine(), "true", caller.getFile().getRelativePath()
