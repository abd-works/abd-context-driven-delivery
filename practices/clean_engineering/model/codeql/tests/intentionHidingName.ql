/**
 * @kind problem
 * @id cdd/practice-graph/test/intentionHidingName
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Name nm
where intentionHidingName(f, nm)
select nm, nm.getId()
