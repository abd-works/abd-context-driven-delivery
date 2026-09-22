/**
 * @name keep-operations-small-focused
 * @kind problem
 * @id cdd/practice-graph/keep-operations-small-focused
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where inSubject(f) and longOperation(f)
select f,
  "Operation '" + f.getName() + "' is " + operationLineCount(f).toString() +
    " lines (max 20).", f
