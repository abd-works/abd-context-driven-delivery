/**
 * @name use-thorough-e2e-tests
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity model
 * @node function
 * @id stories/model/use-thorough-e2e-tests
 */

import javascript
import subject_filter
import model

from CallExpr call, string message, AstNode contributor
where
  inSubject(call) and
  specFile(call.getFile()) and
  call.getCalleeName() = ["deleteMany", "deleteAll", "clearAll"] and
  message = "Blanket delete wipes the entire collection. Delete only the aggregate roots this test created." and
  contributor = call
select call, message, contributor
