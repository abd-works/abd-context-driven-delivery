/**
 * @name use-ubiquitous-language
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity tactics
 * @node class
 * @id ddd/tactics/use-ubiquitous-language
 */

import javascript
import subject_filter
import model

from ClassDefinition cls, string suffix, string message, AstNode contributor
where
  inSubject(cls) and
  technicalSuffix(suffix) and
  cls.getName().matches("%" + suffix) and
  message = "Class '" + cls.getName() + "' uses the technical suffix '" + suffix + "'." and
  contributor = cls
select cls, message, contributor
