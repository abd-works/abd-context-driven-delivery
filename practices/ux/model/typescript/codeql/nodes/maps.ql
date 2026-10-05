/**
 * @name maps
 * @kind problem
 * @id cdd/ux/nodes/maps
 */

import javascript

from File f
where none()
select f.getRelativePath(), "UxMap", "UxMap", "ux", f.getRelativePath(), 1, 1, "discovery"
