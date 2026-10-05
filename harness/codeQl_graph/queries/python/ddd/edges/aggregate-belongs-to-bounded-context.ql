/**
 * @name aggregate-belongs-to-bounded-context
 * @kind problem
 * @id cdd/ddd/edges/aggregate-belongs-to-bounded-context
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
