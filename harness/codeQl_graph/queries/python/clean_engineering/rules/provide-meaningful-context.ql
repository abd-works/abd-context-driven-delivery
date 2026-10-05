/**
 * @name provide-meaningful-context
 * @kind problem
 * @id cdd/clean_engineering/rules/provide-meaningful-context
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Parameter param
where
  rule = "provide-meaningful-context" and
  param = method.getAnArg() and
  param.asName().getId().regexpMatch(".*[0-9]$") and
  node = nodeId("clean_engineering", "Parameter", functionPath(method), param.asName().getId()) and
  violation = ruleViolation(rule, node, "Parameter '" + param.asName().getId() + "' is numbered.")
select rule, node, violation
