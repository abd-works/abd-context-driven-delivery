/**
 * @name aggregate-owns-value-objects
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-value-objects
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
