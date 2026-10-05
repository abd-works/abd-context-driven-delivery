/**
 * @name eliminate-duplication
 * @kind problem
 * @id cdd/clean_engineering/rules/eliminate-duplication
 */

import python
import graph_rule

from string rule, string node, string violation, Function left, Function right
where
  rule = "eliminate-duplication" and
  left != right and
  left.getScope() = right.getScope() and
  left.getName() != right.getName() and
  (
    left.getName().matches("%" + right.getName()) or
    right.getName().matches("%" + left.getName())
  ) and
  node = nodeId("clean_engineering", "Operation", functionPath(left), left.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + left.getName() + "' duplicates '" + right.getName() + "'.")
select rule, node, violation
