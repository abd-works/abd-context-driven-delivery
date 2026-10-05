/**
 * @name entity-root-associates-entities
 * @kind problem
 * @id cdd/ddd/edges/entity-root-associates-entities
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
