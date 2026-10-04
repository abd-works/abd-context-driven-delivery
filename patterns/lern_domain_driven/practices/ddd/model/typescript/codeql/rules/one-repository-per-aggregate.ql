/**
 * @name one-repository-per-aggregate
 * @practice ddd
 * @pattern lern_domain_driven
 * @fidelity tactics
 * @node class
 * @id ddd/tactics/one-repository-per-aggregate
 */

import javascript
import subject_filter
import model

predicate repositoryDeclaration(AstNode node, string name, File f) {
  exists(ClassDefinition cls |
    node = cls and
    name = cls.getName() and
    f = cls.getFile() and
    repositoryType(name)
  )
  or
  exists(InterfaceDefinition iface |
    node = iface and
    name = iface.getName() and
    f = iface.getFile() and
    repositoryType(name)
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(string name, File f |
    repositoryDeclaration(subject, name, f) and
    inSubject(subject) and
    contributor = subject and
    (
      (
        clientFile(f) and
        message =
          "Repository '" + name +
            "' belongs on the aggregate. The client hosts browser behaviour; it does not declare a repository."
      )
      or
      (
        name.matches("%Node%") and
        message =
          "Repository '" + name +
            "' keeps the Repository suffix only. Node names the domain host class in *-node.ts, not the collection."
      )
      or
      exists(AstNode other, string otherName, File otherFile |
        repositoryDeclaration(other, otherName, otherFile) and
        otherFile.getParentContainer() = f.getParentContainer() and
        f.getRelativePath().regexpMatch("src/[^/]+/.*") and
        name < otherName and
        message =
          "Folder '" + f.getParentContainer().getBaseName() + "' declares '" + name +
            "' and '" + otherName + "'. One aggregate has one Repository."
      )
    )
  )
select subject, message, contributor
