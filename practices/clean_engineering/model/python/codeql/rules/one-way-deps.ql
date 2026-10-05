/**
 * @name one-way-deps
 * @kind problem
 * @id cdd/clean_engineering/rules/one-way-deps
 */

import python
import graph_rule

from string rule, string node, string violation, Import imp, Module other
where
  rule = "one-way-deps" and
  imp.getAnImportedModuleName() = other.getName() and
  exists(Import back | back.getEnclosingModule() = other and back.getAnImportedModuleName() = imp.getEnclosingModule().getName()) and
  node = nodeId("clean_engineering", "Module", slash(imp.getEnclosingModule().getFile().getRelativePath()), imp.getEnclosingModule().getName()) and
  violation = ruleViolation(rule, node, "Module '" + imp.getEnclosingModule().getName() + "' imports '" + other.getName() + "' both ways.")
select rule, node, violation
