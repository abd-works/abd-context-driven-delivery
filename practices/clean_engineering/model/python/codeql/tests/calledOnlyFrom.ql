/**
 * @kind problem
 * @id cdd/practice-graph/test/calledOnlyFrom
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Class cls
where calledOnlyFrom(f, cls)
select f, f.getName(), cls
