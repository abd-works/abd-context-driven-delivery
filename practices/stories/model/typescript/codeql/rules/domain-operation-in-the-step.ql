/**
 * @name domain-operation-in-the-step
 * @kind problem
 * @id paradise/domain-operation-in-the-step
 * @problem.severity warning
 */

import javascript

predicate isStepCallback(Function fn) {
  exists(CallExpr call |
    call.getCalleeName() = ["given", "when", "then", "and", "but"] and
    call.getAnArgument() = fn
  )
}

MethodCallExpr soleDomainCall(Function helper) {
  helper.getNumBodyStmt() = 1 and
  (
    result = helper.getABodyStmt().(ReturnStmt).getExpr() or
    result = helper.getABodyStmt().(ReturnStmt).getExpr().(AwaitExpr).getOperand() or
    result = helper.getABodyStmt().(ExprStmt).getExpr() or
    result = helper.getABodyStmt().(ExprStmt).getExpr().(AwaitExpr).getOperand() or
    result = helper.getABodyStmt().(ExprStmt).getExpr().(AssignExpr).getRhs() or
    result = helper.getABodyStmt().(ExprStmt).getExpr().(AssignExpr).getRhs().(AwaitExpr).getOperand()
  )
  or
  helper.getNumBodyStmt() = 0 and
  (
    result = helper.getBody() or
    result = helper.getBody().(AwaitExpr).getOperand()
  )
}

from Function helper, MethodCallExpr call
where
  helper.getFile().getBaseName().regexpMatch(".*\\.story\\.(shared|domain\\.spec|server\\.spec)\\.ts") and
  exists(helper.getName()) and
  not isStepCallback(helper) and
  call = soleDomainCall(helper)
select helper,
  "Helper '" + helper.getName() +
    "' only wraps one domain call. Write that call in the Given, When, or Then step.",
  call
