/**
 * @name map-owns-contexts
 * @kind problem
 * @id cdd/ux/edges/map-owns-contexts
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
