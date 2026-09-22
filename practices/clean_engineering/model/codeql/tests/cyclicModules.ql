/**
 * @kind problem
 * @id cdd/practice-graph/test/cyclicModules
 * @problem.severity warning
 */

import python
import subject_filter
import model

from File a, File b
where cyclicModules(a, b)
select a, a.getRelativePath(), b
