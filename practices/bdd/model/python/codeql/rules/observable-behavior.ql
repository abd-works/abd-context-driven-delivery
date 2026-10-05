/**
 * @name observable-behavior
 * @kind problem
 * @id cdd/bdd/rules/observable-behavior
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, Attribute access
where
  rule = "observable-behavior" and
  call.getFunc().(Name).getId() = "expect" and
  access = call.getArg(0) and
  access.getName().matches("_%") and
  not access.getName().matches("__%") and
  node = nodeId("bdd", "Observation", slash(call.getLocation().getFile().getRelativePath()), access.getName()) and
  violation = ruleViolation(rule, node, "Assertion observes a private attribute instead of stakeholder-visible behaviour.")
select rule, node, violation
