/**
 * @kind problem
 * @id cdd/practice-graph/test/numberedParameter
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where numberedParameter(f, p)
select f, f.getName(), p
