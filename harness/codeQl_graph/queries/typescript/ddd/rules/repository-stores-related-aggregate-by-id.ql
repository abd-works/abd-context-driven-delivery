/**
 * @name repository-stores-related-aggregate-by-id
 * @kind problem
 * @id cdd/ddd/rules/repository-stores-related-aggregate-by-id
 */

import javascript
import graph_rule

from string rule, string node, string violation, FieldDefinition field
where
  rule = "repository-stores-related-aggregate-by-id" and
  field.getInit() instanceof NewExpr and
  node = nodeId("ddd", "Operation", fileOf(field), field.getName()) and
  violation = ruleViolation(rule, node, "Field '" + field.getName() + "' stores another aggregate.")
select rule, node, violation
