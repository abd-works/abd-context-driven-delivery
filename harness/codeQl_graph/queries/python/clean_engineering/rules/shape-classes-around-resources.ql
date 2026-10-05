/**
 * @name shape-classes-around-resources
 * @kind problem
 * @id cdd/clean_engineering/rules/shape-classes-around-resources
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "shape-classes-around-resources" and
  not exists(Function method | method = cls.getAMethod() and not method.getName() = "__init__") and
  exists(AnnAssign field | field.getScope() = cls) and
  node = nodeId("clean_engineering", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' only holds data.")
select rule, node, violation
