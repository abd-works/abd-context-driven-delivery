/**
 * @name avoid-vague-parameter-names
 * @kind problem
 * @id cdd/clean_engineering/rules/avoid-vague-parameter-names
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Parameter param
where
  rule = "avoid-vague-parameter-names" and
  param = method.getAnArg() and
  (
    param.asName().getId() = "data" or
    param.asName().getId() = "options" or
    param.asName().getId() = "info"
  ) and
  node = nodeId("clean_engineering", "Parameter", functionPath(method), param.asName().getId()) and
  violation = ruleViolation(rule, node, "Parameter '" + param.asName().getId() + "' is a vague name.")
select rule, node, violation
