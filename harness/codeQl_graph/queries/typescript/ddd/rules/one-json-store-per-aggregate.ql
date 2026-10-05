/**
 * @name one-json-store-per-aggregate
 * @kind problem
 * @id cdd/ddd/rules/one-json-store-per-aggregate
 */

import javascript
import graph_rule

from string rule, string node, string violation, StringLiteral store
where
  rule = "one-json-store-per-aggregate" and
  store.getValue() = "db.json" and
  node = nodeId("ddd", "Module", fileOf(store), "db.json") and
  violation = ruleViolation(rule, node, "Aggregates share db.json.")
select rule, node, violation
