/**
 * @name constants-not-magic-strings
 * @kind problem
 * @id cdd/clean_engineering/rules/constants-not-magic-strings
 */

import javascript
import graph_rule

from string rule, string node, string violation, Function func, StringLiteral lit
where
  rule = "constants-not-magic-strings" and
  lit.getEnclosingFunction() = func and
  exists(BinaryExpr test | test.getOperator() = "===" and test.getAnOperand() = lit) and
  node = nodeId("clean_engineering", "Operation", fileOf(func), func.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + func.getName() + "' compares the literal '" + lit.getValue() + "'.")
select rule, node, violation
