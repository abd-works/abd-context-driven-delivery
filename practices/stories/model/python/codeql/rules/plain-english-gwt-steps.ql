/**
 * @name plain-english-gwt-steps
 * @kind problem
 * @id cdd/stories/rules/plain-english-gwt-steps
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "plain-english-gwt-steps" and
  (
    call.getFunc().(Name).getId() = "given" or
    call.getFunc().(Name).getId() = "when" or
    call.getFunc().(Name).getId() = "then"
  ) and
  label = call.getArg(0).(StringLiteral).getS() and
  label.regexpMatch("[A-Za-z_][A-Za-z0-9_]*") and
  node = nodeId("stories", "Step", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Step '" + label + "' is a code identifier, not a plain-English sentence.")
select rule, node, violation
