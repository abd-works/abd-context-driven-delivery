/**
 * @name context-belongs-to-description
 * @kind problem
 * @id cdd/bdd/edges/context-belongs-to-description
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
