/**
 * @name initialize-from-fixture-then-seed
 * @kind problem
 * @id paradise/initialize-from-fixture-then-seed
 * @problem.severity warning
 */

import javascript

from NewExpr construction, string typeName
where
  construction.getFile().getBaseName().regexpMatch(".*\\.story\\.(shared|domain\\.spec|server\\.spec)\\.ts") and
  typeName = construction.getCalleeName() and
  typeName = ["AccountCredentials", "Customer", "Identity", "Address", "Billing", "Onboarding"]
select construction,
  "Construct '" + typeName +
    "' in examples/ and seed it from the story. A story test initializes from a fixture.",
  construction
