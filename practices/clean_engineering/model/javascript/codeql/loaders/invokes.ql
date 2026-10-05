/**
 * @name Practice graph invokes
 * @kind problem
 * @id cdd/practice-graph/invokes
 */

import javascript
import subject_filter
import members

from MethodDefinition caller, CallExpr call
where
  classOperation(caller) and
  call.getEnclosingFunction() = caller.getBody() and
  exists(call.getCalleeName())
select caller.getDeclaringType().getName() + "." + caller.getName(),
  call.getCalleeName() + "." + call.getCalleeName(), call.getLocation().getStartLine(), "true",
  caller.getFile().getRelativePath()
