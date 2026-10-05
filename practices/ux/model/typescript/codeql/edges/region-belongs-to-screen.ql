/**
 * @name region-belongs-to-screen
 * @kind problem
 * @id cdd/ux/edges/region-belongs-to-screen
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
