/**
 * @kind problem
 * @id cdd/practice-graph/test/missingSeamOrConstraint
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m, string doc
where missingSeamOrConstraint(m) and moduleDocString(m, doc)
select m, doc
