/**
 * @name region-owns-controls
 * @kind problem
 * @id cdd/ux/edges/region-owns-controls
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
