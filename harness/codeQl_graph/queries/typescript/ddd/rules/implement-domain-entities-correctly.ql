/**
 * @name implement-domain-entities-correctly
 * @kind problem
 * @id cdd/ddd/rules/implement-domain-entities-correctly
 */

import javascript
import graph_rule

from string rule, string node, string violation, ClassDefinition cls
where
  rule = "implement-domain-entities-correctly" and
  exists(cls.getConstructor()) and
  not exists(MethodDeclaration method |
    method = cls.getAMethod() and
    method.getName() != "constructor"
  ) and
  node = nodeId("ddd", "OoadClass", fileOf(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' has no domain operation.")
select rule, node, violation
