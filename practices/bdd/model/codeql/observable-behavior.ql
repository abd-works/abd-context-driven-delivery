/**
 * @name observable-behavior
 * @kind problem
 * @id cdd/practice-graph/observable-behavior
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Call call
where inSubject(call) and observesPrivate(call)
select call, "Assertion observes a private attribute instead of stakeholder-visible behaviour.", call
