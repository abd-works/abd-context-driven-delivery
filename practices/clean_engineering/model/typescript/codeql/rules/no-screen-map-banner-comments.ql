/**
 * @name no-screen-map-banner-comments
 * @kind problem
 * @id cdd/clean_engineering/rules/no-screen-map-banner-comments
 */

import javascript
import graph_rule

from string rule, string node, string violation, Comment comment
where
  rule = "no-screen-map-banner-comments" and
  comment.getText().matches("%Screen:%") and
  node = nodeId("clean_engineering", "Module", slash(comment.getLocation().getFile().getRelativePath()), "Screen") and
  violation = ruleViolation(rule, node, "Comment maps a screen.")
select rule, node, violation
