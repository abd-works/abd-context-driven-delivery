/**
 * @name use-thorough-e2e-tests
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity acceptance_tests
 * @node function
 * @id stories/acceptance_tests/use-thorough-e2e-tests
 */

import javascript
import subject_filter
import model

from CallExpr call, string message, AstNode contributor
where
  inSubject(call) and
  call.getCalleeName() = "deleteMany" and
  message = "Blanket delete wipes the entire collection. Delete only the aggregate roots this test created." and
  contributor = call
select call, message, contributor
