/**
 * @name missing-module-context
 * @kind problem
 * @id cdd/clean_engineering/rules/missing-module-context
 */

import python
import graph_rule

from string rule, string node, string violation, Class cls
where
  rule = "missing-module-context" and
  not exists(Comment comment |
    comment.getLocation().getFile() = cls.getLocation().getFile() and
    comment.getContents().matches("%module-context%")
  ) and
  node = nodeId("clean_engineering", "OoadClass", classPath(cls), cls.getName()) and
  violation = ruleViolation(rule, node, "Class '" + cls.getName() + "' has no module context.")
select rule, node, violation
