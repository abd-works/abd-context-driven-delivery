/**
 * @kind problem
 * @id cdd/practice-graph/test/bareExcept
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, ExceptStmt ex
where bareExcept(f, ex)
select f, f.getName(), ex
