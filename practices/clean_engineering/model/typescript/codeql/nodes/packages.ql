/**
 * @name packages
 * @kind problem
 * @id cdd/ce/nodes/packages
 */

import javascript
import ce

from ClassDefinition cls, string package, string mod
where
  domainClass(cls) and
  mod = moduleOf(cls) and
  package = packageOfFile(classFile(cls))
select packageId(mod, package), package, "Package", "clean_engineering", "src/" + mod + "/" + package, 1, 1,
  "discovery"
