/**
 * @name content-types
 * @kind problem
 * @id cdd/ux/nodes/content-types
 */

import javascript

from File f
where none()
select f.getRelativePath(), "ContentType", "ContentType", "ux", f.getRelativePath(), 1, 1
