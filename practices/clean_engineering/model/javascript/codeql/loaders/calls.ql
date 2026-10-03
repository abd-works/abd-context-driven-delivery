/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls
 */

import javascript
import subject_filter

from MethodDefinition caller, CallExpr call, string calleeName
where
  inSubject(caller) and
  call.getEnclosingFunction() = caller.getBody() and
  calleeName = call.getCalleeName() and
  exists(calleeName)
select caller.getDeclaringType().getName(), caller.getName(),
  call.getCalleeName(), calleeName, call.getFile().getRelativePath(),
  caller.getFile().getRelativePath()
