/**
 * @kind problem
 * @id cdd/practice-graph/test/publicName
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls
where publicName(cls.getName()) and cls.getName() = "CartManager"
select cls, cls.getName()
