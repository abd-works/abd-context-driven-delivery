/**
 * @kind problem
 * @id cdd/practice-graph/test/domainParameter
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Parameter p
where domainParameter(f, p) and f.getName() = "place"
select f, p.getName()
