/**
 * @kind problem
 * @id cdd/practice-graph/test/inSource
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f
where inSource(f) and f.getName() = "huge"
select f, f.getName()
