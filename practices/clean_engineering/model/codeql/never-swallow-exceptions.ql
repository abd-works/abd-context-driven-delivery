/**
 * @name never-swallow-exceptions
 * @kind problem
 * @id cdd/practice-graph/never-swallow-exceptions
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, ExceptStmt ex
where inSubject(f) and swallowedExcept(f, ex)
select f, "Operation '" + f.getName() + "' catches an exception and ignores it.", ex
