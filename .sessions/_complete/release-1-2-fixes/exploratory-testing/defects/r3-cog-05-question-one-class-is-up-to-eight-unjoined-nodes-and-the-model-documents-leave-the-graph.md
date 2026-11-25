# Question: one class is two to eight nodes that no edge joins (a DDD node and a Clean Engineering node for the same file and name, one per language, one per folder), and with the code loaded no node comes from the domain model or the class models, so nothing says which are one thing

- **Charter:** Round 3, second pass - the knowledge graph of the combined project, check 4
- **Tester:** Cog
- **Story:** epic "Map Work Into Knowledge Graph"; no scenario covers one class seen by two practices, or a model document beside the code that implements it.
- **Module and class:** `cdd_guidance/practices/ddd/model/graph_reading.py` and `cdd_guidance/practices/clean_engineering/model/graph_reading.py` (each makes its own node for a class of the DDD folders; neither links to the other), `harness/graph/graph.py` `Graph.return_nodes` (the `name` filter).
- **Severity:** question (which of these are meant to be one node, or joined by an edge such as `implements` or `realizes`?)
- **Related:** r3-sparky-09 part 2 (a model root leaves when code names it), r3-widget-08 (class model documents give no class), r3-bolt-01, r3-bolt-05.

## Steps
Sandbox `C:\dev\_et\round3\cog\work` (a copy of the combined Bookshop), throwaway cdd server: `sh C:/dev/_et/round3/cog/drv/go.sh q1.json` and `e1.json`.

    graph.load_files {"folder": "C:/dev/_et/round3/cog/work", "practices": ["stories","ddd","ux","clean_engineering","bdd"], "files": [".context","story_tests","src","catalogue","ordering","fulfilment","bookshop","ux"]}
    graph.return_nodes {"filter": {"name": "Order"}}
    graph.load_files {... "practices": ["ddd"], "files": [".context/domain-model.md"]}  then graph.inventory {}
    graph.load_files {... "practices": ["ddd"], "files": [".context/domain-model.md","ordering","catalogue","fulfilment"]}  then graph.return_nodes {"filter": {"practices": ["ddd"], "paths": [".context"]}}

## Expected
Not known. A person asking for "Order" expects one thing with its model, its code in each language, its specs and its stories around it, or several nodes joined by edges that say how they relate.

## Actual
1. `name: Order` answers 8 nodes: `ddd:EntityRoot:ordering/order/order.py:Order` and `clean_engineering:OoadClass:ordering/order/order.py:Order` (the same class of the same file), the same pair for `order.ts`, and `OoadClass` for `src/bookshop/order.py`, `src/bookshop/order.ts`, `src/ordering/order.py`, `src/ordering/order.ts`. No edge joins any two of them. In the whole graph 17 class names are held by 84 nodes, and 34 classes of the DDD folders are each a DDD node and a Clean Engineering node with no edge between the two. No edge of any kind runs between DDD and another practice.
2. The filter matches the whole name with its case: `Order` leaves out the aggregate `ddd:Aggregate:ordering/order` (named `order`), the stories Submit Order, Pack Order, Cancel Order and Mark Order Shipped, the describe `an order`, and every step that names the Order; `order` answers 13 nodes, 11 of them parameters and properties.
3. `.context/domain-model.md` alone gives 16 nodes (4 Aggregate, 4 EntityRoot, 4 Repository, 3 ValueObject, 1 Entity). Loaded with the three DDD code folders, `paths: [".context"]` answers the same 16 from the document and the inventory counts 4 roots, not 8: the code's roots are not added. In the load of the whole project no node at all has `.context/domain-model.md` as its file: the 16 are gone and the code's nodes stand in their place (aggregates named `cart`, `order`, `book`, `shipment` after folders). So the model's class is never in the graph together with the code class that implements it, and which one a load keeps depends on what else is loaded.
4. The three Clean Engineering class models (`src/*/.context/*-model.md`, 8 classes) give no node (r3-widget-08), so "model class to code class" has nothing at the model end either.
5. Each story test file is also a `bdd:Spec` node (10 of the 16 Specs), with no Description or Observation below it except `confirm-order.story.ui.spec.ts`, whose two describes are named for the stories View Order Confirmation and Cancel Order; no edge joins those to the Story nodes.

## Tier that should catch it
Once answered, unit: the DDD and Clean Engineering graph readings' specs with one class read by both.
