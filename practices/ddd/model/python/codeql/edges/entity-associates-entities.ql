/**
 * @name entity-associates-entities
 * @kind problem
 * @id cdd/ddd/edges/entity-associates-entities
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
