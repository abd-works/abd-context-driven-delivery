/**
 * @name interaction-belongs-to-control
 * @kind problem
 * @id cdd/ux/edges/interaction-belongs-to-control
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
