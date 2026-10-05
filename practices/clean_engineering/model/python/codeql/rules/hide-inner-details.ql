/**
 * @name hide-inner-details
 * @kind problem
 * @id cdd/clean_engineering/rules/hide-inner-details
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Attribute access
where
  rule = "hide-inner-details" and
  access.getScope() = method and
  access.getName().matches("_%") and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' reads '" + access.getName() + "'.")
select rule, node, violation
