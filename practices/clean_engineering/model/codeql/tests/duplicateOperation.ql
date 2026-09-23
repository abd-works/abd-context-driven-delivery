/**
 * @kind problem
 * @id cdd/practice-graph/test/duplicateOperation
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function a, Function b
where duplicateOperation(a, b)
select a, a.getName()
