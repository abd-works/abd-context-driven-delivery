/**
 * @name fluent-operation-returns-next-aggregate
 * @kind problem
 * @id paradise/fluent-operation-returns-next-aggregate
 * @problem.severity warning
 */

import javascript

predicate storyTest(File file) {
  file.getRelativePath().regexpMatch(".*tests/.*")
}

predicate scenarioCallback(Function callback) {
  exists(CallExpr scenario |
    scenario.getCalleeName() = "scenario" and
    scenario.getArgument(1) = callback
  )
}

predicate inScenario(Expr node, Function callback) {
  scenarioCallback(callback) and
  (
    node.getEnclosingFunction() = callback
    or
    node.getEnclosingFunction().getEnclosingContainer().getFunctionBoundary() = callback
    or
    node.getEnclosingFunction()
        .getEnclosingContainer()
        .getFunctionBoundary()
        .(Function)
        .getEnclosingContainer()
        .getFunctionBoundary() = callback
  )
}

predicate customerRepositoryCreate(MethodCallExpr createCall) {
  storyTest(createCall.getFile()) and
  createCall.getMethodName() = "create" and
  (
    createCall.getReceiver().(VarAccess).getName() = "customerRepository"
    or
    createCall.getReceiver().(PropAccess).getPropertyName() = "customerRepository"
  )
}

predicate accountCustomerId(PropAccess customerId) {
  customerId.getPropertyName() = "customerId" and
  customerId.getBase().(VarAccess).getName() = "accountCredentials" and
  exists(MethodCallExpr assertion |
    assertion.getCalleeName() = ["toBe", "toEqual", "toStrictEqual"] and
    (
      assertion.getAnArgument() = customerId
      or
      exists(CallExpr expectCall |
        expectCall = assertion.getReceiver() and
        expectCall.getCalleeName() = "expect" and
        expectCall.getAnArgument() = customerId
      )
    )
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(MethodCallExpr createCall, Function callback |
    customerRepositoryCreate(createCall) and
    inScenario(createCall, callback) and
    (
      exists(MethodCallExpr storeCall |
        storeCall.getMethodName() = "storeCustomerId" and
        inScenario(storeCall, callback) and
        subject = createCall and
        contributor = storeCall and
        message =
          "Story calls customerRepository.create and then storeCustomerId. Call the operation on the aggregate and use the aggregate it returns."
      )
      or
      exists(PropAccess customerId |
        accountCustomerId(customerId) and
        inScenario(customerId, callback) and
        subject = customerId and
        contributor = createCall and
        message =
          "Story asserts accountCredentials.customerId as the association after create. Use the customer object the operation returns."
      )
    )
  )
select subject, message, contributor
