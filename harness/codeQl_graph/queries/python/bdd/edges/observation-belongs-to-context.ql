/**
 * @name observation-belongs-to-context
 * @kind problem
 * @id cdd/bdd/edges/observation-belongs-to-context
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
