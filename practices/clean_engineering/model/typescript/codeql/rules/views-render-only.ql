/**
 * @name views-render-only
 * @kind problem
 * @id cdd/clean_engineering/rules/views-render-only
 */

import javascript
import graph_rule

from string rule, string node, string violation, Function func
where
  rule = "views-render-only" and
  func.getName() = "destination" and
  fileOf(func).matches("%.tsx") and
  node = nodeId("clean_engineering", "Operation", fileOf(func), func.getName()) and
  violation = ruleViolation(rule, node, "View decides the next page.")
select rule, node, violation
