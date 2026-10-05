/**
 * @name domain-objects-own-their-attributes
 * @kind problem
 * @id cdd/ddd/rules/domain-objects-own-their-attributes
 */

import javascript
import graph_rule

from string rule, string node, string violation, FieldDeclaration field
where
  rule = "domain-objects-own-their-attributes" and
  field.getName() = ["simType", "iccid"] and
  node = nodeId("ddd", "Operation", fileOf(field), field.getName()) and
  violation = ruleViolation(rule, node, "Field '" + field.getName() + "' belongs to another aggregate.")
select rule, node, violation
