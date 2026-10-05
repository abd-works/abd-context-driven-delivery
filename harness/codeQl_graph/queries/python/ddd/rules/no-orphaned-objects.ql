/**
 * @name no-orphaned-objects
 * @kind problem
 * @id cdd/ddd/rules/no-orphaned-objects
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "no-orphaned-objects" and
  count(Class other | other.getLocation().getFile() = cls.getLocation().getFile()) = 1 and
  not exists(Call call, Class other |
    other != cls and
    call.getLocation().getFile() = cls.getLocation().getFile() and
    call.getFunc().(Name).getId() = other.getName()
  ) and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' has no relationship to another type.")
select rule, node, violation
