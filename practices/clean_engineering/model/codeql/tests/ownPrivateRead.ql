/**
 * @kind problem
 * @id cdd/practice-graph/test/ownPrivateRead
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Attribute attr
where ownPrivateRead(f, attr)
select f, f.getName(), attr
