/**
 * @name aggregate-owns-domain-services
 * @kind problem
 * @id cdd/ddd/edges/aggregate-owns-domain-services
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
