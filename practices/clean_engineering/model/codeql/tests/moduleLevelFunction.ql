/**
 * @kind problem
 * @id cdd/practice-graph/test/moduleLevelFunction
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where moduleLevelFunction(f) and f.getName() = "_extended_price"
select f, f.getName()
