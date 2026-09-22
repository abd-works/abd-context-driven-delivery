/**
 * @name private-method-naming
 * @kind problem
 * @id cdd/practice-graph/private-method-naming
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Call call
where inSubject(f) and leakedPrivate(f, call)
select f, "Private operation '" + f.getName() + "' is called from outside its definition.", call
