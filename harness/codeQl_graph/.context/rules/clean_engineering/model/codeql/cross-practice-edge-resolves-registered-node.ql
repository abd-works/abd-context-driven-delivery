/**
 * @name cross-practice-edge-resolves-registered-node
 * @kind problem
 * @id cdd/clean_engineering/model/cross-practice-edge-resolves-registered-node
 * @problem.severity warning
 */

import javascript

from MethodDefinition method
where
  method.getName() = "load_edges" and
  exists(MethodCallExpr call |
    call.getEnclosingFunction() = method.getBody() and
    call.getMethodName() = "get" and
    call.getReceiver().(PropAccess).getPropertyName() = "byId"
  ) and
  not exists(MethodCallExpr registered |
    registered.getEnclosingFunction() = method.getBody() and
    registered.getCalleeName() = "registered"
  )
select method,
  "load_edges resolves a node_id already registered on another practice of this CodeQLKnowledgeGraph.",
  method
