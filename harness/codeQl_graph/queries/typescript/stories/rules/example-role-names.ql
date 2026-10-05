/**
 * @name example-role-names
 * @kind problem
 * @id cdd/stories/rules/example-role-names
 */

import javascript
import graph_rule

from string rule, string node, string violation, VarDecl decl
where
  rule = "example-role-names" and
  decl.getName().matches("valid%") and
  node = nodeId("stories", "Module", fileOf(decl), decl.getName()) and
  violation = ruleViolation(rule, node, "Example '" + decl.getName() + "' is named for a role.")
select rule, node, violation
