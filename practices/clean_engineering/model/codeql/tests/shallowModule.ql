/**
 * @kind problem
 * @id cdd/practice-graph/test/shallowModule
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module m
where shallowModule(m)
select m, m.getFile().getRelativePath()
