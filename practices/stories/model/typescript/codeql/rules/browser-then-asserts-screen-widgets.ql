/**
 * @name browser-then-asserts-screen-widgets
 * @kind problem
 * @id cdd/stories/rules/browser-then-asserts-screen-widgets
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call
where
  rule = "browser-then-asserts-screen-widgets" and
  call.getCalleeName() = "getByTestId" and
  node = nodeId("stories", "Step", fileOf(call), "getByTestId") and
  violation = ruleViolation(rule, node, "Then asserts a test id.")
select rule, node, violation
