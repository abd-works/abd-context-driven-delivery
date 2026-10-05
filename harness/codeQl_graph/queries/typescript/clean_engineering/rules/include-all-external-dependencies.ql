/**
 * @name include-all-external-dependencies
 * @kind problem
 * @id cdd/clean_engineering/rules/include-all-external-dependencies
 */

import javascript
import graph_rule

import semmle.javascript.JSON

predicate packageDeclares(File source, string moduleName) {
  exists(JsonValue root |
    root.isTopLevel() and
    root.getJsonFile().getBaseName() = "package.json" and
    source.getParentContainer*() = root.getJsonFile().getParentContainer() and
    exists(root.getPropValue("dependencies").getPropValue(moduleName))
  )
}

from string rule, string node, string violation, ImportDeclaration decl
where
  rule = "include-all-external-dependencies" and
  not packageDeclares(decl.getFile(), decl.getImportedPathString()) and
  node = nodeId("clean_engineering", "Module", fileOf(decl), decl.getImportedPathString()) and
  violation = ruleViolation(rule, node, "Import '" + decl.getImportedPathString() + "' is missing from package.json.")
select rule, node, violation
