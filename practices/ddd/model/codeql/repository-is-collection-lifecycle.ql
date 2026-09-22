/**
 * @name repository-is-collection-lifecycle
 * @kind problem
 * @id cdd/practice-graph/repository-is-collection-lifecycle
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls
where inSubject(cls) and thinRepository(cls)
select cls,
  "Class '" + cls.getName() + "' is named Repository without collection lifecycle operations.", cls
