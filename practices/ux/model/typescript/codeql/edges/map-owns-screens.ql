/**
 * @name map-owns-screens
 * @kind problem
 * @id cdd/ux/edges/map-owns-screens
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
