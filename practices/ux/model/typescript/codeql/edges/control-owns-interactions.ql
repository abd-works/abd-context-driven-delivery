/**
 * @name control-owns-interactions
 * @kind problem
 * @id cdd/ux/edges/control-owns-interactions
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
