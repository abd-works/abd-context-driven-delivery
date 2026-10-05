/**
 * @name interactions
 * @kind problem
 * @id cdd/ux/nodes/interactions
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Interaction", "Interaction", "ux", f.getRelativePath(), 1, 1, "discovery"
