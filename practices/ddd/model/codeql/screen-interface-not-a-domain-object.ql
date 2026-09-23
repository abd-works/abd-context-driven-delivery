/**
 * @name screen-interface-not-a-domain-object
 * @kind problem
 * @id cdd/practice-graph/screen-interface-not-a-domain-object
 * @problem.severity warning
 */

import python
import model

from Class cls
where screenDriver(cls)
select cls,
  "Type '" + cls.getName() +
    "' looks like a screen driver (open + shown-state). Keep screen verbs off the domain object."
