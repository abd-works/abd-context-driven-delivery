/**
 * @kind problem
 * @id cdd/practice-graph/test/untypedPublicParameter
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where untypedPublicParameter(f, p)
select f, f.getName(), p
