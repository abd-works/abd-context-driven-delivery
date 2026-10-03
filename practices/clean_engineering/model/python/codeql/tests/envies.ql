/**
 * @kind problem
 * @id cdd/practice-graph/test/envies
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where envies(f, p)
select f, f.getName(), p
