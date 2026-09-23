/**
 * @kind problem
 * @id cdd/practice-graph/test/mixedNamingFunction
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m, Function f
where mixedNamingFunction(m, f)
select f, f.getName()
