/**
 * @kind problem
 * @id cdd/practice-graph/test/privateAttributeRead
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Attribute attr
where privateAttributeRead(f, attr)
select f, f.getName(), attr
