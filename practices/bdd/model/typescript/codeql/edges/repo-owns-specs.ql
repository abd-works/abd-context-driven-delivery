/**
 * @name repo-owns-specs
 * @kind problem
 * @id cdd/bdd/edges/repo-owns-specs
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
