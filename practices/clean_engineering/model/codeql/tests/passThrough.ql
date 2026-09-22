/**
 * @kind problem
 * @id cdd/practice-graph/test/passThrough
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where passThrough(f)
select f, f.getName()
