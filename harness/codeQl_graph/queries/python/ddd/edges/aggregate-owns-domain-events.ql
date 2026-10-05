/**
 * @name aggregate-owns-domain-events
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-domain-events
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
