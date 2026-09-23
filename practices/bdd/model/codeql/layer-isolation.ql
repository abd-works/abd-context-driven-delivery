/**
 * @name layer-isolation
 * @kind problem
 * @id cdd/practice-graph/layer-isolation
 * @problem.severity warning
 */

import python
import model

from Call c, string target
where relativeInternalMock(c, target)
select c,
  "Mock targets internal module '" + target +
    "'. Only mock external boundaries (APIs, databases, third-party services)."
