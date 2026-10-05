/**
 * @name building-blocks-fidelity-requires-tactical-stereotype
 * @kind problem
 * @id cdd/ddd/rules/building-blocks-fidelity-requires-tactical-stereotype
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "building-blocks-fidelity-requires-tactical-stereotype" and
  not exists(cls.getABase()) and
  not exists(Function method | method = cls.getAMethod()) and
  not cls.getName().regexpMatch(".*(Entity|Value|Aggregate|Repository|Service|Event|Root)$") and
  node = nodeId("ddd", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' is missing a tactical stereotype.")
select rule, node, violation
