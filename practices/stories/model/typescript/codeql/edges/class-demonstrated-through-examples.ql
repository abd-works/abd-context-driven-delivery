/**
 * @name class-demonstrated-through-examples
 * @kind problem
 * @id cdd/stories/edges/class-demonstrated-through-examples
 */

import javascript
import stories

from string file, string name, ClassDefinition cls, string parent, string child
where
  cls.getName() = exampleReturnClassName(file, name) and
  parent = classNodeId(cls) and
  child = exampleId(file, name)
select parent, child, "demonstratedThrough", 6, "relationship"
