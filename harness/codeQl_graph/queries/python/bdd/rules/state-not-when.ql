/**
 * @name state-not-when
 * @kind problem
 * @id cdd/bdd/rules/state-not-when
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "state-not-when" and
  call.getFunc().(Name).getId() = "context" and
  label = call.getArg(0).(StringLiteral).getS() and
  label.toLowerCase().matches("when %") and
  node = nodeId("bdd", "Context", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Nested state is named with 'when' instead of a condition.")
select rule, node, violation
