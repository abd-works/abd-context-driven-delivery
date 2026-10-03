import javascript
import subject_filter

predicate domainImport(ImportDeclaration imp) {
  exists(string path | path = imp.getImportedPathString() |
    path.matches("%/domain/%") or path.matches("%/stories/%")
  )
}

predicate uxOnlyAdapter(ImportDeclaration imp) {
  exists(string path | path = imp.getImportedPathString() |
    path.matches("%adapter%") or path.matches("%fake%") or path.matches("%stub%")
  ) and
  not domainImport(imp)
}

predicate gotoLiteral(StringLiteral s) { s.getValue() = "data-goto" }

predicate hasGoto(File file) { exists(StringLiteral s | s.getFile() = file and gotoLiteral(s)) }
