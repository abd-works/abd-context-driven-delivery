/**
 * @name use-explicit-dependencies
 * @kind problem
 * @id cdd/clean_engineering/rules/use-explicit-dependencies
 */

import python
import graph_rule

from string rule, string node, string violation, Class owner, Call created
where
  rule = "use-explicit-dependencies" and
  created.getScope() = owner.getAMethod() and
  created.getFunc().(Name).getId() != owner.getName() and
  exists(Class other | other != owner and other.getName() = created.getFunc().(Name).getId()) and
  node = nodeId("clean_engineering", "OoadClass", classPath(owner), owner.getName()) and
  violation = ruleViolation(rule, node, "Class '" + owner.getName() + "' constructs '" + created.getFunc().(Name).getId() + "'.")
select rule, node, violation
