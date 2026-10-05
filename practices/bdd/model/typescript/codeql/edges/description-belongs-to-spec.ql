/**
 * @name description-belongs-to-spec
 * @kind problem
 * @id cdd/bdd/edges/description-belongs-to-spec
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
