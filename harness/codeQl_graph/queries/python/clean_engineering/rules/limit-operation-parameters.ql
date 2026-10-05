/**
 * @name limit-operation-parameters
 * @kind problem
 * @id cdd/clean_engineering/rules/limit-operation-parameters
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "limit-operation-parameters" and
  count(Parameter param |
    param = method.getAnArg() and
    param.asName().getId() != "self" and
    param.asName().getId() != "cls"
  ) > 2 and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' takes more than two parameters.")
select rule, node, violation
