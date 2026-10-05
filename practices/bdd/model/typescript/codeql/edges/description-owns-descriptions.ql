/**
 * @name description-owns-descriptions
 * @kind problem
 * @id cdd/bdd/edges/description-owns-descriptions
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
