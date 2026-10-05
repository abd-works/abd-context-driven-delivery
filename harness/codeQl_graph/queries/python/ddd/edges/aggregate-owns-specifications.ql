/**
 * @name aggregate-owns-specifications
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-specifications
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
