/**
 * @name specs
 * @kind problem
 * @id cdd/bdd/nodes/specs
 */

import javascript

from File f
where none()
select f.getRelativePath(), "Spec", "Spec", "bdd", f.getRelativePath(), 1, 1
