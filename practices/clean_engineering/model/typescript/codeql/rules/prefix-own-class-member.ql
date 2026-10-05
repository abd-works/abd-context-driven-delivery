/**
 * @name prefix-own-class-member
 * @kind problem
 * @id cdd/clean_engineering/rules/prefix-own-class-member
 */

import javascript
import graph_rule

from string rule, string node, string violation, FieldDeclaration field
where
  rule = "prefix-own-class-member" and
  not field.getName().regexpMatch("_.*") and
  node = nodeId("clean_engineering", "Operation", fileOf(field), field.getName()) and
  violation = ruleViolation(rule, node, "Field '" + field.getName() + "' has no underscore prefix.")
select rule, node, violation
