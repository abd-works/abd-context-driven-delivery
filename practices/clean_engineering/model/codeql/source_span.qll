import python

/** First line of the node in source. */
int sourceStart(AstNode n) { result = n.getLocation().getStartLine() }

/**
 * Last line of a class or function, including nested statements and methods.
 * `getLocation().getEndLine()` on a Class is often only the header line.
 */
int sourceEnd(Scope scope) {
  result =
    max(int line |
      exists(AstNode n |
        (n = scope or n.getScope+() = scope) and
        line = n.getLocation().getEndLine()
      )
    )
}
