/**
 * @name observations
 * @kind problem
 * @id cdd/bdd/nodes/observations
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Observation", "Observation", "bdd", f.getRelativePath(), 1, 1, "specification"
