/**
 * @name private-cross-aggregate-step
 * @kind problem
 * @id paradise/private-cross-aggregate-step
 * @problem.severity warning
 */

import javascript

predicate calledOnlyFromVerify(MethodCallExpr call) {
  exists(MethodDefinition caller |
    call.getEnclosingFunction() = caller.getBody() and
    caller.getDeclaringClass().getName() = "AccountCredentials" and
    caller.getName() = "verify"
  )
}

from AstNode subject, string message, MethodDefinition contributor
where
  exists(MethodDefinition method, ClassDefinition type |
    subject = method and
    contributor = method and
    method.getDeclaringClass() = type and
    method.getName() = "newCustomer" and
    (
      type.getName().matches("%Repository") and
      message =
        "AccountRepository.newCustomer is a public repository operation. Keep newCustomer private on AccountCredentials and call it only from verify."
      or
      type.getName() = "AccountCredentials" and
      not method.isPrivate() and
      message =
        "AccountCredentials.newCustomer must be private. verify is the public operation."
    )
  )
  or
  exists(MethodCallExpr call |
    subject = call and
    call.getCalleeName() = "newCustomer" and
    not calledOnlyFromVerify(call) and
    message =
      "newCustomer is a private cross-aggregate step. Call it only from AccountCredentials.verify." and
    contributor.getName() = "newCustomer" and
    contributor.getDeclaringClass().getName() = "AccountCredentials"
  )
select subject, message, contributor
