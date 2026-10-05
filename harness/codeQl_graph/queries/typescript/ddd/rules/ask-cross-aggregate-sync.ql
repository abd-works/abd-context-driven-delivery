/**
 * @name ask-cross-aggregate-sync
 * @kind problem
 * @id cdd/ddd/rules/ask-cross-aggregate-sync
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodDeclaration method, NewExpr created
where
  rule = "ask-cross-aggregate-sync" and
  created.getEnclosingFunction() = method.getBody() and
  exists(ClassDefinition cls | cls.getName() = created.getCalleeName()) and
  node = nodeId("ddd", "Operation", fileOf(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' constructs another aggregate.")
select rule, node, violation
