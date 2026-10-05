/**
 * @name owns
 * @kind problem
 * @id cdd/bdd/edges/owns
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "owns", 1, "direct"
