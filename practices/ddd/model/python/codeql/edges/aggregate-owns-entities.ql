/**
 * @name aggregate-owns-entities
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-entities
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
