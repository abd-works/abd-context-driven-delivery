/**
 * @name context-owns-observations
 * @kind problem
 * @id cdd/bdd/edges/context-owns-observations
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
