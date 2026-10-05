import javascript

bindingset[path]
string slash(string path) { result = path.replaceAll("\\", "/") }

bindingset[rule, node, details]
string ruleViolation(string rule, string node, string details) {
  result = rule + " violation suspected at " + node + " " + details
}

bindingset[practice, kind, path, name]
string nodeId(string practice, string kind, string path, string name) {
  result = practice + ":" + kind + ":" + slash(path) + ":" + name
}

string fileOf(AstNode node) { result = slash(node.getFile().getRelativePath()) }
