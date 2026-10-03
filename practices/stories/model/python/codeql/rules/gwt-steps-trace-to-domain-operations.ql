/**
 * @name gwt-steps-trace-to-domain-operations
 * @practice stories
 * @fidelity scenarios
 * @node steps
 * @id stories/scenarios/gwt-steps-trace-to-domain-operations
 * @connection clean_engineering.class
 */

import python
import subject_filter
import model

from Call call, string keyword, string label
where
  inSubject(call) and
  stepCall(call, keyword) and
  label = call.getArg(0).(StringLiteral).getValue() and
  not exists(Class cls | label.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%"))
select call, "Step '" + label + "' does not mention a domain type from the rest of the graph.", call
