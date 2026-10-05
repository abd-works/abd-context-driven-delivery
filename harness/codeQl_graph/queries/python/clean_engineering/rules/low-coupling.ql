/**
 * @name low-coupling
 * @kind problem
 * @id cdd/clean_engineering/rules/low-coupling
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Attribute access
where
  rule = "low-coupling" and
  access.getScope() = method and
  access.getName().matches("_%") and
  not access.getObject().(Name).getId() = "self" and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' reaches through '" + access.getName() + "'.")
select rule, node, violation
