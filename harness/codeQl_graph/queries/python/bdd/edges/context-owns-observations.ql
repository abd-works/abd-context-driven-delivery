/**
 * @name context-owns-observations
 * @kind problem
 * @id cdd/bdd/edges/context-owns-observations
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
