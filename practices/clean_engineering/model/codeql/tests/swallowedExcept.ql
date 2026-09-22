/**
 * @kind problem
 * @id cdd/practice-graph/test/swallowedExcept
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, ExceptStmt ex
where swallowedExcept(f, ex)
select f, f.getName(), ex
