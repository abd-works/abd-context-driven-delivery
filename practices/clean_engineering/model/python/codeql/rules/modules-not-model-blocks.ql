/**
 * @name modules-not-model-blocks
 * @kind problem
 * @id cdd/clean_engineering/rules/modules-not-model-blocks
 */

import python
import graph_rule

from string rule, string node, string violation, Comment comment
where
  rule = "modules-not-model-blocks" and
  (
    comment.getContents().matches("%------%") or
    comment.getContents().toLowerCase().matches("%live instance%")
  ) and
  node = nodeId("clean_engineering", "Module", slash(comment.getLocation().getFile().getRelativePath()), comment.getLocation().getFile().getStem()) and
  violation = ruleViolation(rule, node, "Module context dumps a model block.")
select rule, node, violation
