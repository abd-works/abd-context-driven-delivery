/**
 * @name private-method-naming
 * @kind problem
 * @id cdd/ddd/rules/private-method-naming
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Call call
where
  rule = "private-method-naming" and
  method.getName().regexpMatch("_.*") and
  not method.getName().regexpMatch("__.*") and
  call.getFunc().(Attribute).getName() = method.getName() and
  call.getLocation().getFile() = method.getLocation().getFile() and
  not call.getFunc().(Attribute).getObject().(Name).getId() = "self" and
  node = nodeId("ddd", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Private operation '" + method.getName() + "' is called from outside its class.")
select rule, node, violation
