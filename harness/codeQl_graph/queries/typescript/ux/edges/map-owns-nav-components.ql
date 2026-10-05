/**
 * @name map-owns-nav-components
 * @kind problem
 * @id cdd/ux/edges/map-owns-nav-components
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
