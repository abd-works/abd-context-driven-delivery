/**
 * @kind problem
 * @id cdd/practice-graph/test/accessorOperation
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where accessorOperation(f)
select f, f.getName()
