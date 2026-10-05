/**
 * @name scaffold-test-scripts
 * @kind problem
 * @id cdd/stories/rules/scaffold-test-scripts
 */

import javascript
import graph_rule

from string rule, string node, string violation, File vitest
where
  rule = "scaffold-test-scripts" and
  vitest.getBaseName() = "vitest.config.ts" and
  not exists(File playwright |
    playwright.getBaseName() = "playwright.config.ts" and
    playwright.getParentContainer() = vitest.getParentContainer()
  ) and
  node = nodeId("stories", "Module", slash(vitest.getRelativePath()), vitest.getStem()) and
  violation = ruleViolation(rule, node, "Scaffold has vitest and no playwright config.")
select rule, node, violation
