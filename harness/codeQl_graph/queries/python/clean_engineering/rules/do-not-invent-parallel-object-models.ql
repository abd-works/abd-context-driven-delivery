/**
 * @name do-not-invent-parallel-object-models
 * @kind problem
 * @id cdd/clean_engineering/rules/do-not-invent-parallel-object-models
 */

import python
import graph_rule

from string rule, string node, string violation, Class copy, Class original
where
  rule = "do-not-invent-parallel-object-models" and
  copy != original and
  copy.getName().matches("%Entry") and
  node = nodeId("clean_engineering", "OoadClass", classPath(copy), copy.getName()) and
  violation = ruleViolation(rule, node, "Class '" + copy.getName() + "' restates another type.")
select rule, node, violation
