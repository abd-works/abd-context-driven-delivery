/**
 * @name screen-interface-not-a-domain-object
 * @kind problem
 * @id cdd/ddd/rules/screen-interface-not-a-domain-object
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls, Function method
where
  rule = "screen-interface-not-a-domain-object" and
  method = cls.getAMethod() and
  (method.getName() = "open" or method.getName() = "isShowing" or method.getName() = "is_showing") and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' looks like a screen driver.")
select rule, node, violation
