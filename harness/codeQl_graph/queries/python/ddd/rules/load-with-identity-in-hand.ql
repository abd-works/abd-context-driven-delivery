/**
 * @name load-with-identity-in-hand
 * @kind problem
 * @id cdd/ddd/rules/load-with-identity-in-hand
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "load-with-identity-in-hand" and
  method.getName() = "load" and
  not exists(Parameter param | param = method.getAnArg() and param.asName().getId() != "self") and
  node = nodeId("ddd", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation 'load' takes no identity.")
select rule, node, violation
