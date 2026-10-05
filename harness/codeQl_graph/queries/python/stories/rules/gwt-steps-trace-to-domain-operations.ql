/**
 * @name gwt-steps-trace-to-domain-operations
 * @kind problem
 * @id cdd/stories/rules/gwt-steps-trace-to-domain-operations
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "gwt-steps-trace-to-domain-operations" and
  (
    call.getFunc().(Name).getId() = "given" or
    call.getFunc().(Name).getId() = "when" or
    call.getFunc().(Name).getId() = "then"
  ) and
  label = call.getArg(0).(StringLiteral).getS() and
  not exists(Class cls | label.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%")) and
  node = nodeId("stories", "Step", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Step '" + label + "' does not mention a domain type.")
select rule, node, violation
