/**
 * @name layer-separation
 * @kind problem
 * @id cdd/practice-graph/layer-separation
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where inSubject(f) and passThrough(f)
select f, "Operation '" + f.getName() + "' only forwards a single call.", f
