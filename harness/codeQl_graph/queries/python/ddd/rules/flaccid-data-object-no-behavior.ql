/**
 * @name flaccid-data-object-no-behavior
 * @kind problem
 * @id cdd/ddd/rules/flaccid-data-object-no-behavior
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "flaccid-data-object-no-behavior" and
  not exists(Function method | method = cls.getAMethod() and method.getName() != "__init__") and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' is a field bag.")
select rule, node, violation
