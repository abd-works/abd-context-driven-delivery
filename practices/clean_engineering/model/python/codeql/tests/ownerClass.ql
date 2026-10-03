/**
 * @kind problem
 * @id cdd/practice-graph/test/ownerClass
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Class cls
where ownerClass(f, cls) and cls.getName() = "CartManager"
select f, f.getName(), cls
