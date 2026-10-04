/**
 * @name domain-fixture-example-files
 * @kind problem
 * @id paradise/domain-fixture-example-files
 * @problem.severity warning
 */

import javascript

from File example
where
  example.getRelativePath().regexpMatch("(?i).*tests/.*/examples/.*") and
  example
      .getRelativePath()
      .regexpMatch("(?i).*(mavenir|cognito|twilio|persona|vouchera|zendesk|amplify|apple|gateway|service).*")
select example,
  "Example file '" + example.getBaseName() +
    "' names a vendor or system. Name story examples for Paradise domain fixtures.",
  example
