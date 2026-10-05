/**
 * @name simplify-control-flow
 * @kind problem
 * @id cdd/clean_engineering/rules/simplify-control-flow
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "simplify-control-flow" and
  count(If ifstmt | ifstmt.getScope*() = method) > 2 and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' nests control flow.")
select rule, node, violation
