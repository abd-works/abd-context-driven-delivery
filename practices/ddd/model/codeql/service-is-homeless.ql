/**
 * @name service-is-homeless
 * @kind problem
 * @id cdd/practice-graph/service-is-homeless
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class cls
where inSubject(cls) and homelessService(cls)
select cls, "Class '" + cls.getName() + "' parks verbs that belong on a domain object.", cls
