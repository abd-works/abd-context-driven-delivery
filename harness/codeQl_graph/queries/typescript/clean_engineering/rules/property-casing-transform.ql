/**
 * @name property-casing-transform
 * @kind problem
 * @id cdd/clean_engineering/rules/property-casing-transform
 */

import javascript
import graph_rule

from string rule, string node, string violation, FieldDeclaration field
where
  rule = "property-casing-transform" and
  field.getName().regexpMatch(".*_.*") and
  node = nodeId("clean_engineering", "Operation", fileOf(field), field.getName()) and
  violation = ruleViolation(rule, node, "Field '" + field.getName() + "' uses snake case.")
select rule, node, violation
