/**
 * @name entity-belongs-to-aggregate
 * @kind problem
 * @id cdd/ddd/edges/entity-belongs-to-aggregate
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
