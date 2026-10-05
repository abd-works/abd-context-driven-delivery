/**
 * @name belongs-to
 * @kind problem
 * @id cdd/ux/edges/belongs-to
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
