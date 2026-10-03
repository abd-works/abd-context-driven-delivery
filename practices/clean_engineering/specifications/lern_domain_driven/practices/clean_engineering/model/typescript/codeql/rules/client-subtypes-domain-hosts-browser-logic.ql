/**
 * @name client-subtypes-domain-hosts-browser-logic
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node class
 * @id clean_engineering/code/client-subtypes-domain-hosts-browser-logic
 */

import javascript
import subject_filter
import model

from ClassDefinition cls, string folderSlug, string domainName, string message, AstNode contributor
where
  inSubject(cls) and
  folderSlug = cls.getFile().getParentContainer().getBaseName() and
  cls.getFile().getBaseName() = folderSlug + "-client.tsx" and
  exists(File core |
    core.getParentContainer() = cls.getFile().getParentContainer() and
    core.getBaseName() = folderSlug + ".ts"
  ) and
  domainName = pascalFromSlug(folderSlug) and
  cls.getName() = domainName + "Client" and
  not cls.getSuperClass().(VarAccess).getName() = domainName and
  message =
    cls.getName() + " subtypes " + domainName +
      " declared in the domain file for this folder." and
  contributor = cls.getIdentifier()
select cls, message, contributor
