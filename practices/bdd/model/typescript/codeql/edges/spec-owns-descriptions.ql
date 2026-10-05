/**
 * @name spec-owns-descriptions
 * @kind problem
 * @id cdd/bdd/edges/spec-owns-descriptions
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
