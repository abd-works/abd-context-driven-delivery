/**
 * @name state-not-when
 * @kind problem
 * @id cdd/practice-graph/state-not-when
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Call call
where inSubject(call) and whenContext(call)
select call, "Nested state is named with 'when' instead of a condition.", call
