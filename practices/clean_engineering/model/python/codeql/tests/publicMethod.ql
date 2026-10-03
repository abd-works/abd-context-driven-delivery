/**
 * @kind problem
 * @id cdd/practice-graph/test/publicMethod
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls, Function method
where publicMethod(cls, method) and cls.getName() = "CartManager"
select cls, method.getName()
