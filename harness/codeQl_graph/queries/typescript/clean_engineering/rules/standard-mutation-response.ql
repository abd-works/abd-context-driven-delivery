/**
 * @name standard-mutation-response
 * @kind problem
 * @id cdd/clean_engineering/rules/standard-mutation-response
 */

import javascript
import graph_rule

from string rule, string node, string violation, Property prop
where
  rule = "standard-mutation-response" and
  prop.getName() = "success" and
  node = nodeId("clean_engineering", "Operation", fileOf(prop), "success") and
  violation = ruleViolation(rule, node, "Response carries a success flag.")
select rule, node, violation
