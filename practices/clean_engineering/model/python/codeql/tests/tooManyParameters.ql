/**
 * @kind problem
 * @id cdd/practice-graph/test/tooManyParameters
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where tooManyParameters(f)
select f, f.getName()
