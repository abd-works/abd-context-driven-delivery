/**
 * @kind problem
 * @id cdd/practice-graph/test/proceduralDoer
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class doer
where proceduralDoer(doer)
select doer, doer.getName()
