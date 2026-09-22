/**
 * @name screen-interface-not-a-domain-object
 * @kind problem
 * @id cdd/practice-graph/screen-interface-not-a-domain-object
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls
where inSubject(cls) and screenClass(cls)
select cls, "Class '" + cls.getName() + "' looks like a screen driver, not a domain type.", cls
