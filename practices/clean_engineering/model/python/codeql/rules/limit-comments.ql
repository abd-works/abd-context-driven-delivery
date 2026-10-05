/**
 * @name limit-comments
 * @kind problem
 * @id cdd/clean_engineering/rules/limit-comments
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls, Comment comment
where
  rule = "limit-comments" and
  comment.getLocation().getFile() = cls.getLocation().getFile() and
  node = nodeId("clean_engineering", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' is explained by a comment.")
select rule, node, violation
