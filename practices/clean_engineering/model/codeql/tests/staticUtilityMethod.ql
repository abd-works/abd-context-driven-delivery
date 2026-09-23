/**
 * @kind problem
 * @id cdd/practice-graph/test/staticUtilityMethod
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where staticUtilityMethod(f)
select f, f.getName()
