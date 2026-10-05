/**
 * @name extensions-live-with-the-domain
 * @kind problem
 * @id cdd/clean_engineering/rules/extensions-live-with-the-domain
 */

import python
import graph_rule

from string rule, string node, string violation, Class child, Class parent
where
  rule = "extensions-live-with-the-domain" and
  child.getABase().(Name).getId() = parent.getName() and
  slash(child.getLocation().getFile().getRelativePath()).matches("%/framework/%") and
  slash(parent.getLocation().getFile().getRelativePath()).matches("%/domain/%") and
  node = nodeId("clean_engineering", "OoadClass", classPath(child), child.getName()) and
  violation = ruleViolation(rule, node, "Class '" + child.getName() + "' extends domain '" + parent.getName() + "' from the framework.")
select rule, node, violation
