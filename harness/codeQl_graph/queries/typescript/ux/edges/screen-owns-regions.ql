/**
 * @name screen-owns-regions
 * @kind problem
 * @id cdd/ux/edges/screen-owns-regions
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
