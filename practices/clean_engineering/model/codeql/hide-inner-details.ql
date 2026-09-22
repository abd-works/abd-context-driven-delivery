/**
 * @name hide-inner-details
 * @kind problem
 * @id cdd/practice-graph/hide-inner-details
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Attribute attr
where inSubject(f) and privateAttributeRead(f, attr)
select f,
  "Operation '" + f.getName() + "' reads private attribute '" + attr.getName() + "'.", attr
