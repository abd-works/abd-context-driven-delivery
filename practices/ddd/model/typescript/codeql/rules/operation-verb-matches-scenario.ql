/**
 * @name operation-verb-matches-scenario
 * @kind problem
 * @id paradise/operation-verb-matches-scenario
 * @problem.severity warning
 */

import javascript

predicate stepSaysVerify(CallExpr step) {
  step.getCalleeName() = ["given", "when", "then", "and", "but"] and
  exists(string text |
    text = step.getArgument(0).getStringValue()
    or
    text = step.getArgument(0).(TemplateLiteral).getElement(_).(TemplateElement).getValue()
  |
    text.regexpMatch("(?i).*verif.*")
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(MethodDefinition method |
    subject = method and
    contributor = method and
    method.getDeclaringClass().getName() = "AccountCredentials" and
    method.isPublic() and
    method.getName() = "activate" and
    message =
      "AccountCredentials.activate is not the scenario verb. The step says the user verifies the account, so the operation is verify."
  )
  or
  exists(MethodCallExpr call, CallExpr step |
    subject = call and
    contributor = step and
    stepSaysVerify(step) and
    call.getEnclosingFunction() = step.getArgument(1) and
    call.getCalleeName() = "activate" and
    message =
      "The step says the user verifies the account, so call verify, not activate."
  )
select subject, message, contributor
