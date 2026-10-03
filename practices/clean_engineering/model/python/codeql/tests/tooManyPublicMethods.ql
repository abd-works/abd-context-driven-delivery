/**
 * @kind problem
 * @id cdd/practice-graph/test/tooManyPublicMethods
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls
where tooManyPublicMethods(cls)
select cls, cls.getName()
