/**
 * @name node-hosts-entity
 * @kind problem
 * @id cdd/lern/ddd/edges/node-hosts-entity
 */

import javascript
import lern

from ClassDefinition node, ClassDefinition root, string child
where
  domainNodeClass(node) and
  dddClass(root, "EntityRoot", child, _, _, _, _) and
  extendsNamed(node, root.getName())
select domainNodeId(node), child, "hosts", 5, "relationship"
