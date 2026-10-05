/**
 * @name initialize-from-fixture-then-seed
 * @kind problem
 * @id cdd/stories/rules/initialize-from-fixture-then-seed
 */

import javascript
import graph_rule

from string rule, string node, string violation, NewExpr created
where
  rule = "initialize-from-fixture-then-seed" and
  not exists(created.getEnclosingFunction()) and
  node = nodeId("stories", "Module", fileOf(created), created.getCalleeName()) and
  violation = ruleViolation(rule, node, "Fixture constructs '" + created.getCalleeName() + "' at the top level.")
select rule, node, violation
