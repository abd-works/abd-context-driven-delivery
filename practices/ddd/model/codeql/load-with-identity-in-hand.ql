/**
 * @name load-with-identity-in-hand
 * @kind problem
 * @id cdd/practice-graph/load-with-identity-in-hand
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where inSubject(f) and loadWithoutIdentity(f)
select f, "Operation 'load' takes no identity.", f
