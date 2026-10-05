/**
 * @name transition-belongs-to-map
 * @kind problem
 * @id cdd/ux/edges/transition-belongs-to-map
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
