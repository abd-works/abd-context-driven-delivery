/**
 * @name map-owns-content-types
 * @kind problem
 * @id cdd/ux/edges/map-owns-content-types
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
