/**
 * @name repository-accesses-entity-root
 * @kind problem
 * @id cdd/ddd/edges/repository-accesses-entity-root
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
