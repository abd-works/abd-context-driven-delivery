# knowledge_graph — CodeQL graph load (sketch)

fidelity: behavior
status: signatures named; load still lives in CodeQL.populate and arrangeListedClassChildren until development fills these observations

CodeQL node queries register nodes. CodeQL edge queries relate those nodes. Edges carry order and immediate, so a class lists relative children first, then operations, then a properties collapse. A story lists examples from demonstrates edges.

=========
theme: bdd behavior
---------

a practice graph
  that has been populated from CodeQL
    it should register every node from node queries
    it should relate every edge from edge queries

a class
  that has relative, operation, and property children from CodeQL
    it should list relative children first
    it should list operations after relatives
    it should list a properties collapse after operations

a story
  that has demonstrates edges
    it should list examples from those demonstrates edges
