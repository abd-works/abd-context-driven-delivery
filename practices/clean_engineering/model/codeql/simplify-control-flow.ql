/**
 * @name simplify-control-flow
 * @kind problem
 * @id cdd/practice-graph/simplify-control-flow
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where inSubject(f) and deeplyNested(f)
select f, "Operation '" + f.getName() + "' nests control flow more than three levels.", f
