/**
 * @kind problem
 * @id cdd/practice-graph/test/longOperation
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where longOperation(f)
select f, f.getName()
