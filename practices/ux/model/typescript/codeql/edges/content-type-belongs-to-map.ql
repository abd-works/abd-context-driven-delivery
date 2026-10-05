/**
 * @name content-type-belongs-to-map
 * @kind problem
 * @id cdd/ux/edges/content-type-belongs-to-map
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
