/**
 * @name module-owns-packages
 * @kind problem
 * @id cdd/ce/edges/module-owns-packages
 */

import javascript
import clean_engineering.ce

from ClassDefinition cls, string package, string mod
where
  domainClass(cls) and
  mod = moduleOf(cls) and
  package = packageOfFile(classFile(cls))
select moduleId(mod), packageId(mod, package), "owns", 2, "direct"
