/**
 * @name use-typed-signatures
 * @kind problem
 * @id cdd/clean_engineering/rules/use-typed-signatures
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Parameter param
where
  rule = "use-typed-signatures" and
  param = method.getAnArg() and
  param.asName().getId() != "self" and
  param.getAnnotation().(Name).getId() = "dict" and
  node = nodeId("clean_engineering", "Parameter", functionPath(method), param.asName().getId()) and
  violation = ruleViolation(rule, node, "Parameter '" + param.asName().getId() + "' is typed as dict.")
select rule, node, violation
