/**
 * @name construct-repository-at-the-caller
 * @kind problem
 * @id cdd/ddd/rules/construct-repository-at-the-caller
 */

import javascript
import graph_rule

from string rule, string node, string violation, NewExpr created
where
  rule = "construct-repository-at-the-caller" and
  created.getCalleeName().matches("%Repository") and
  not exists(created.getEnclosingFunction()) and
  node = nodeId("ddd", "Module", fileOf(created), created.getCalleeName()) and
  violation = ruleViolation(rule, node, "Repository '" + created.getCalleeName() + "' is constructed at the top level.")
select rule, node, violation
