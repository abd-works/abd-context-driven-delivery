/**
 * @name contexts
 * @kind problem
 * @id cdd/bdd/nodes/contexts
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Context", "Context", "bdd", f.getRelativePath(), 1, 1
