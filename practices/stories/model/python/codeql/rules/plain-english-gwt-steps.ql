/**
 * @name plain-english-gwt-steps
 * @practice stories
 * @fidelity scenarios
 * @node steps
 * @id stories/scenarios/plain-english-gwt-steps
 */

import python
import subject_filter
import model

from Call call, string keyword, string label
where
  inSubject(call) and
  stepCall(call, keyword) and
  label = call.getArg(0).(StringLiteral).getValue() and
  identifierStep(label)
select call, "Step '" + label + "' is a code identifier, not a plain-English sentence.", call
