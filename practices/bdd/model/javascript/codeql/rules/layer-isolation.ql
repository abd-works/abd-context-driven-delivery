/**
 * @name layer-isolation
 * @practice bdd
 * @fidelity development
 * @node observation
 * @id bdd/development/layer-isolation
 */

import javascript
import model

from CallExpr c, string target
where relativeInternalMock(c, target)
select c,
  "Mock targets internal module '" + target +
    "'. Only mock external boundaries (APIs, databases, third-party services)."
