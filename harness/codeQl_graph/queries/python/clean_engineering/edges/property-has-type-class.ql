/**
 * @name property-has-type-class
 * @kind problem
 * @id cdd/ce/edges/property-has-type-class
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"