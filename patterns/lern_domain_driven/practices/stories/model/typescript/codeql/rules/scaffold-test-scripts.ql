/**
 * @name scaffold-test-scripts
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity model
 * @node module
 * @id stories/model/scaffold-test-scripts
 */

import javascript
import subject_filter
import model

from File sentinel, TopLevel top, string message, AstNode contributor
where
  sentinel.getBaseName() = "vitest.config.ts" and
  not exists(File pw | pw.getBaseName() = "playwright.config.ts") and
  top.getFile() = sentinel and
  inSubject(top) and
  message = "Missing playwright.config.ts. Keep Vitest and Playwright runners separate." and
  contributor = top
select top, message, contributor
