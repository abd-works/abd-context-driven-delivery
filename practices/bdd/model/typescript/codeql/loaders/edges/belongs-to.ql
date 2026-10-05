/**
 * @name belongs-to
 * @kind problem
 * @id cdd/bdd/edges/belongs-to
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
