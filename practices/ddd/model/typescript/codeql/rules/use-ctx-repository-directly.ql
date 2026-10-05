/**
 * @name use-ctx-repository-directly
 * @kind problem
 * @id cdd/ddd/rules/use-ctx-repository-directly
 */

import javascript
import graph_rule

from string rule, string node, string violation, ReturnStmt ret, PropAccess access
where
  rule = "use-ctx-repository-directly" and
  ret.getExpr() = access and
  access.getBase().(VarAccess).getName() = "ctx" and
  node = nodeId("ddd", "Operation", fileOf(ret), access.getPropertyName()) and
  violation = ruleViolation(rule, node, "Return hands back ctx." + access.getPropertyName() + ".")
select rule, node, violation
