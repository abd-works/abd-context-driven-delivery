/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls
 */

import javascript
import subject_filter
import members

from MethodDefinition caller, CallExpr call, string calleeName
where
  classOperation(caller) and
  call.getEnclosingFunction() = caller.getBody() and
  calleeName = call.getCalleeName() and
  exists(calleeName)
select caller.getDeclaringType().getName(), caller.getName(),
  call.getCalleeName(), calleeName, call.getFile().getRelativePath(),
  caller.getFile().getRelativePath()
