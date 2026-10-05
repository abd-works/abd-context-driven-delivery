/**
 * @name repo-owns-specs
 * @kind problem
 * @id cdd/bdd/edges/repo-owns-specs
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
