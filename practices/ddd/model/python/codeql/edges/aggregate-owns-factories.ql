/**
 * @name aggregate-owns-factories
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-factories
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
