/**
 * @name controls
 * @kind problem
 * @id cdd/ux/nodes/controls
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Control", "Control", "ux", f.getRelativePath(), 1, 1
