/**
 * @name control-belongs-to-region
 * @kind problem
 * @id cdd/ux/edges/control-belongs-to-region
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
