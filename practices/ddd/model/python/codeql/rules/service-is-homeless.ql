/**
 * @name service-is-homeless
 * @kind problem
 * @id cdd/ddd/rules/service-is-homeless
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "service-is-homeless" and
  cls.getName().matches("%Service") and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' parks verbs that belong on a domain object.")
select rule, node, violation
