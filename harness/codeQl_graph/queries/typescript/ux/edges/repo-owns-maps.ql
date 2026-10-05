/**
 * @name repo-owns-maps
 * @kind problem
 * @id cdd/ux/edges/repo-owns-maps
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
