/**
 * @name language-modules-one-section
 * @kind problem
 * @id cdd/clean_engineering/rules/language-modules-one-section
 */

import python
import graph_rule

from string rule, string node, string violation, Comment comment
where
  rule = "language-modules-one-section" and
  comment.getContents().toLowerCase().matches("%modules%") and
  node = nodeId("clean_engineering", "Module", slash(comment.getLocation().getFile().getRelativePath()), comment.getLocation().getFile().getStem()) and
  violation = ruleViolation(rule, node, "Module context has a Modules heading.")
select rule, node, violation
