/**
 * @name entity-has-identity-property
 * @kind problem
 * @id cdd/ddd/edges/entity-has-identity-property
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
