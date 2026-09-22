/**
 * @name use-exceptions-properly
 * @kind problem
 * @id cdd/practice-graph/use-exceptions-properly
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, ExceptStmt ex
where inSubject(f) and bareExcept(f, ex)
select f, "Operation '" + f.getName() + "' uses a bare except.", ex
