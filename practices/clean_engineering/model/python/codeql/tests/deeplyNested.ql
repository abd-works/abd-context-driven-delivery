/**
 * @kind problem
 * @id cdd/practice-graph/test/deeplyNested
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where deeplyNested(f)
select f, f.getName()
