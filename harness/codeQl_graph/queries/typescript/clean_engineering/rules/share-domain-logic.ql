/**
 * @name share-domain-logic
 * @kind problem
 * @id cdd/clean_engineering/rules/share-domain-logic
 */

import javascript
import graph_rule

from string rule, string node, string violation, ImportDeclaration decl
where
  rule = "share-domain-logic" and
  decl.getImportedPathString() = "zod" and
  fileOf(decl).matches("%-node.ts") and
  node = nodeId("clean_engineering", "Module", fileOf(decl), "zod") and
  violation = ruleViolation(rule, node, "Node file imports zod.")
select rule, node, violation
