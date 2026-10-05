/**
 * @name description-belongs-to-description
 * @kind problem
 * @id cdd/bdd/edges/description-belongs-to-description
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "belongsTo", 2, "relationship"
