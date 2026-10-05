/**
 * @name transitions
 * @kind problem
 * @id cdd/ux/nodes/transitions
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Transition", "Transition", "ux", f.getRelativePath(), 1, 1, "discovery"
