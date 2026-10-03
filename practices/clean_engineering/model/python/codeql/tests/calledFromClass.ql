/**
 * @kind problem
 * @id cdd/practice-graph/test/calledFromClass
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Class cls
where calledFromClass(f, cls) and f.getName() = "_extended_price"
select f, cls.getName()
