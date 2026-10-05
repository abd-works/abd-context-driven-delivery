/**
 * @name describe-is-subject-not-internal
 * @kind problem
 * @id cdd/bdd/rules/describe-is-subject-not-internal
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call, string label
where
  rule = "describe-is-subject-not-internal" and
  (call.getCalleeName() = "describe" or call.getCalleeName() = "description") and
  label = call.getArgument(0).(StringLiteral).getValue() and
  (
    label.matches("%Manager%") or label.matches("%Service%") or label.matches("%Runner%") or
    label.matches("%Hub%") or label.matches("%SessionLog%")
  ) and
  node = nodeId("bdd", "Description", fileOf(call), label) and
  violation = ruleViolation(rule, node, "Describe names internal type '" + label + "' instead of a domain subject.")
select rule, node, violation
