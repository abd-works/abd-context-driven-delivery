/**
 * @name deep-module
 * @kind problem
 * @id cdd/clean_engineering/rules/deep-module
 */

import python
import graph_rule

from string rule, string node, string violation, Module mod, int classes
where
  rule = "deep-module" and
  mod.getFile().getRelativePath().matches("%__init__.py") and
  classes = count(Class cls | cls.getLocation().getFile() = mod.getFile()) and
  classes > 1 and
  node = nodeId("clean_engineering", "Module", slash(mod.getFile().getRelativePath()), mod.getFile().getStem()) and
  violation = ruleViolation(rule, node, "Module publishes " + classes.toString() + " classes.")
select rule, node, violation
