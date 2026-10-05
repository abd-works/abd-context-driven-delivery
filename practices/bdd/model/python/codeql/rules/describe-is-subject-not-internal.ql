/**
 * @name describe-is-subject-not-internal
 * @kind problem
 * @id cdd/bdd/rules/describe-is-subject-not-internal
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "describe-is-subject-not-internal" and
  call.getFunc().(Name).getId() = "description" and
  label = call.getArg(0).(StringLiteral).getS() and
  (
    label.matches("%Manager%") or label.matches("%Service%") or label.matches("%Runner%") or
    label.matches("%Hub%") or label.matches("%SessionLog%")
  ) and
  node = nodeId("bdd", "Description", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Describe names internal type '" + label + "' instead of a domain subject.")
select rule, node, violation
