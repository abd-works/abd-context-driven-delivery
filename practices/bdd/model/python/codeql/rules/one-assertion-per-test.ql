/**
 * @name one-assertion-per-test
 * @kind problem
 * @id cdd/bdd/rules/one-assertion-per-test
 */

import python
import graph_rule

from string rule, string node, string violation, With block, Call itCall, string label
where
  rule = "one-assertion-per-test" and
  itCall.getFunc().(Name).getId() = "it" and
  block.getContextExpr() = itCall and
  label = itCall.getArg(0).(StringLiteral).getS() and
  count(Call assertion | assertion.getFunc().(Name).getId() = "expect" and assertion.getParentNode*() = block) > 1 and
  node = nodeId("bdd", "Observation", slash(itCall.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Example has more than one assertion.")
select rule, node, violation
