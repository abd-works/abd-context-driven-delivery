/**
 * @name Practice graph calls
 * @kind problem
 * @id cdd/practice-graph/calls-javascript
 */

import javascript

string baseName(Expr base, MethodDefinition caller) {
  base instanceof ThisExpr and result = caller.getDeclaringType().getName()
  or
  result = base.(VarAccess).getName()
  or
  result = base.(PropAccess).getPropertyName()
}

from MethodDefinition caller, string calleeOwner, string calleeName
where
  exists(caller.getDeclaringType().getName()) and
  exists(caller.getName()) and
  (
    exists(InvokeExpr invoke, PropAccess callee |
      invoke.getEnclosingFunction() = caller and
      callee = invoke.getCallee() and
      calleeName = callee.getPropertyName() and
      calleeOwner = baseName(callee.getBase(), caller)
    )
    or
    exists(PropAccess access |
      access.getEnclosingFunction() = caller and
      not exists(InvokeExpr invoke | invoke.getCallee() = access) and
      calleeName = access.getPropertyName() and
      calleeOwner = baseName(access.getBase(), caller)
    )
  )
select caller.getDeclaringType().getName(), caller.getName(), calleeOwner, calleeName,
  caller.getFile().getRelativePath(), caller.getFile().getRelativePath()
