/**
 * @name keep-classes-single-responsibility
 * @kind problem
 * @id cdd/clean_engineering/rules/keep-classes-single-responsibility
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "keep-classes-single-responsibility" and
  count(Function method | method = cls.getAMethod() and method.getName() != "__init__") > 1 and
  node = nodeId("clean_engineering", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' owns more than one operation.")
select rule, node, violation
