/**
 * @name observation-belongs-to-context
 * @kind problem
 * @id cdd/bdd/edges/observation-belongs-to-context
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
