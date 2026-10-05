/**
 * @name domain-concepts-not-technical-names
 * @kind problem
 * @id cdd/ddd/rules/domain-concepts-not-technical-names
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "domain-concepts-not-technical-names" and
  (
    cls.getName().matches("%Manager") or cls.getName().matches("%Helper") or cls.getName().matches("%Util%")
  ) and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' uses a technical name.")
select rule, node, violation
