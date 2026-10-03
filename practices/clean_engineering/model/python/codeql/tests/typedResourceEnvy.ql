/**
 * @kind problem
 * @id cdd/practice-graph/test/typedResourceEnvy
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p, Class resource
where typedResourceEnvy(f, p, resource)
select f, f.getName(), p
