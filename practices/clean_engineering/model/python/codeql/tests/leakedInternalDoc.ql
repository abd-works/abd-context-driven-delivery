/**
 * @kind problem
 * @id cdd/practice-graph/test/leakedInternalDoc
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m, string doc
where leakedInternalDoc(m) and moduleDocString(m, doc)
select m, doc
