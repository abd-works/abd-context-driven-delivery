/**
 * @name gwt-steps-trace-to-domain-operations
 * @kind problem
 * @id cdd/practice-graph/gwt-steps-trace-to-domain-operations
 * @problem.severity warning
 *
 * Connector: step labels in the subject vs class names in the whole database.
 */

import javascript
import subject_filter
import model

from CallExpr call, string keyword, string label
where
  inSubject(call) and
  stepCall(call, keyword) and
  label = call.getArgument(0).(StringLiteral).getValue() and
  not exists(ClassDefinition cls | label.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%"))
select call, "Step '" + label + "' does not mention a domain type from the rest of the graph.", call
