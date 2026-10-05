/**
 * @name context-owns-contexts
 * @kind problem
 * @id cdd/bdd/edges/context-owns-contexts
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
