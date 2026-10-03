/**
 * @name implement-domain-entities-correctly
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity building_blocks
 * @node class
 * @id ddd/building_blocks/implement-domain-entities-correctly
 */

import javascript
import subject_filter
import model

from ClassDefinition cls, string message, AstNode contributor
where
  inSubject(cls) and
  coreFile(cls.getFile()) and
  not exists(MethodDeclaration m | m = cls.getAMethod() and m.getName() != "constructor") and
  message = "Class '" + cls.getName() + "' holds state but has no behaviour." and
  contributor = cls
select cls, message, contributor
