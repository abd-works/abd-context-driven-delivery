import javascript
import subject_filter
import model

predicate graphRuleHit(AstNode subject, string message, AstNode contributor, string slug) {
  slug = "screen-names-use-domain-terms" and
  exists(StringLiteral title |
    inSubject(title) and
    title.getValue().matches("%Screen") and
    not exists(ClassDefinition cls |
      title.getValue().toLowerCase().matches("%" + cls.getName().toLowerCase() + "%")
    ) and
    subject = title and
    contributor = title and
    message = "Screen title '" + title.getValue() + "' does not use a domain type name."
  )
  or
  slug = "key-interactions-wired" and
  exists(File file, TopLevel top |
    inSubjectPath(file.getRelativePath()) and
    file.getBaseName().matches("%.js") and
    not hasGoto(file) and
    top.getFile() = file and
    subject = top and
    contributor = top and
    message = "Screen module '" + file.getBaseName() + "' has no data-goto interaction wiring."
  )
  or
  slug = "story-domain-js-imported" and
  exists(ImportDeclaration imp |
    inSubject(imp) and
    uxOnlyAdapter(imp) and
    subject = imp and
    contributor = imp and
    message = "UX surface imports a stub adapter instead of story or domain JS."
  )
}
