/**
 * @name contexts
 * @kind problem
 * @id cdd/ux/nodes/contexts
 */

import javascript

from File f
where none()
select f.getRelativePath(), "UxContext", "UxContext", "ux", f.getRelativePath(), 1, 1, "discovery"
