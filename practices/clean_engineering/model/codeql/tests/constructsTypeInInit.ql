/**
 * @kind problem
 * @id cdd/practice-graph/test/constructsTypeInInit
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function init, Class constructed
where constructsTypeInInit(init, constructed)
select init, constructed.getName()
