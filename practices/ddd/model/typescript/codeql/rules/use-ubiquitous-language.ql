/**
 * @name use-ubiquitous-language
 * @kind problem
 * @id cdd/ddd/rules/use-ubiquitous-language
 */

import javascript
import graph_rule

from string rule, string node, string violation, ClassDefinition cls
where
  rule = "use-ubiquitous-language" and
  cls.getName().regexpMatch(".*(Manager|Helper)") and
  node = nodeId("ddd", "OoadClass", fileOf(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' is outside the ubiquitous language.")
select rule, node, violation
