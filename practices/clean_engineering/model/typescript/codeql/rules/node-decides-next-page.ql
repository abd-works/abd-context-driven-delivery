/**
 * @name node-decides-next-page
 * @kind problem
 * @id cdd/clean_engineering/rules/node-decides-next-page
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call
where
  rule = "node-decides-next-page" and
  call.getCalleeName() = "redirect" and
  node = nodeId("clean_engineering", "Operation", fileOf(call), "redirect") and
  violation = ruleViolation(rule, node, "Handler redirects to the next page.")
select rule, node, violation
