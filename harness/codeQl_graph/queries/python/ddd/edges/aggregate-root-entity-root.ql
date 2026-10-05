/**
 * @name aggregate-root-entity-root
 * @kind problem
 * @id cdd/ddd/edges/aggregate-root-entity-root
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
