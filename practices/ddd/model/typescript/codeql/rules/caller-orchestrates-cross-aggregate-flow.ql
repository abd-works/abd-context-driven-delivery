/**
 * @name caller-orchestrates-cross-aggregate-flow
 * @kind problem
 * @id paradise/caller-orchestrates-cross-aggregate-flow
 * @problem.severity warning
 */

import javascript

predicate aggregateRepositorySingleton(string name) {
  name = [
    "customerRepository",
    "onboardingRepository",
    "billingRepository",
    "accountRepository",
  ]
}

predicate orchestrationLayerClass(ClassDefinition type) {
  type.getName().matches("%Repository") and
  type.getFile().getRelativePath().regexpMatch("src/.*\\.ts")
}

predicate persistenceMethod(MethodDefinition method) {
  method.getName() = ["rehydrate", "save", "hydrate", "accountFor", "seed"]
}

predicate relatedAggregateCrud(string name) {
  name = ["load", "rehydrate", "find", "store"]
}

predicate crossRepositorySingletonCall(MethodCallExpr call, string calleeRepo) {
  call.getReceiver().(VarAccess).getName() = calleeRepo and
  aggregateRepositorySingleton(calleeRepo)
}

predicate allowedCrossRepositoryCall(MethodCallExpr call, MethodDefinition caller) {
  persistenceMethod(caller) and
  relatedAggregateCrud(call.getMethodName())
}

from MethodCallExpr call, ClassDefinition repoClass, MethodDefinition caller, string calleeRepo, string message
where
  orchestrationLayerClass(repoClass) and
  call.getEnclosingFunction() = caller.getBody() and
  caller.getDeclaringClass() = repoClass and
  crossRepositorySingletonCall(call, calleeRepo) and
  not allowedCrossRepositoryCall(call, caller) and
  message =
    repoClass.getName() + " calls " + calleeRepo + "." + call.getMethodName() +
      ". Orchestrate related aggregates in routes, views, or the story/client flow; keep each repository aggregate-specific."
select call, message, caller
