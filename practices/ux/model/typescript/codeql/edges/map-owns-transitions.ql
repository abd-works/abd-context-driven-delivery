/**
 * @name map-owns-transitions
 * @kind problem
 * @id cdd/ux/edges/map-owns-transitions
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
