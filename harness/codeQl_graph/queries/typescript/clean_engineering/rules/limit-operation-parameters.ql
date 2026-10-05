/**
 * @name limit-operation-parameters
 * @kind problem
 * @id cdd/ce/rules/limit-operation-parameters
 */

import javascript
import clean_engineering.ce

from string rule, string node, string violation, MethodDefinition method
where
  rule = "limit-operation-parameters" and
  classOperation(method) and
  count(Parameter param | param = method.getBody().getAParameter() and param.getName() != "this") > 2 and
  (
    node = operationId(method) and
    violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' takes more than two parameters.")
    or
    exists(Parameter param |
      param = method.getBody().getAParameter() and
      param.getName() != "this" and
      node = parameterId(method, param) and
      violation = ruleViolation(rule, node, "Parameter '" + param.getName() + "' is one of more than two parameters on '" + method.getName() + "'.")
    )
  )
select rule, node, violation
