/**
 * @name put-logic-on-the-owning-resource
 * @kind problem
 * @id cdd/clean_engineering/rules/put-logic-on-the-owning-resource
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Attribute access
where
  rule = "put-logic-on-the-owning-resource" and
  access.getScope() = method and
  access.getObject() instanceof Name and
  access.getObject().(Name).getId() != "self" and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' works through '" + access.getObject().(Name).getId() + "'.")
select rule, node, violation
