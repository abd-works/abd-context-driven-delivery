/**
 * @name descriptions
 * @kind problem
 * @id cdd/bdd/nodes/descriptions
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Description", "Description", "bdd", f.getRelativePath(), 1, 1, "specification"
