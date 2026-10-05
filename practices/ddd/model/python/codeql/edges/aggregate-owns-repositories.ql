/**
 * @name aggregate-owns-repositories
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-repositories
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
