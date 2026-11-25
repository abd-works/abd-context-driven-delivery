# After one class model is rendered to markdown, every later model rendered to markdown by the same cdd server gets the first model's class names, and a model file is written over with them

- **Charter:** Round 3 - Clean Engineering (modules, model, code) in every format, checks 1, 2 and 4
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers two models rendered one after the other.
- **Module and class:** `cdd_guidance/practices/clean_engineering/model/markdown/markdown_class_model.py` `MarkdownCleanEngineeringModel` (where the failure shows; the cause was not looked for, but the names last for the server's life, so something kept between calls holds the first document's class headings); the file is then saved by `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save`
- **Severity:** wrong result (silent: the answer names the file as if all went well; from drawio or whiteboard the person's own model file is the one written over)

## Steps
Sandbox `C:\dev\_et\round3\widget\work`, session `main`, one throwaway cdd server on the build at 4d47fdf8e: `bash C:\dev\_et\round3\widget\drv\go.sh c4.json` (the same in `c3.json` with the catalogue first). Three models: `src/catalogue` (Catalogue, Book), `src/ordering` (Cart, CartLine, Order, Payment), `src/fulfilment` (Shipment, ExpressShipment : Shipment), each as `.context/<module>-model.md`, `.drawio`, `.whiteboard`, and `<module>.py`, `<module>.ts` rendered from the markdown.

In one server, one after the other:

1. `render.render {"guidance":"clean-engineering-model","format":"markdown","paths":["src/ordering/ordering.py"]}`
2. `render.render {"guidance":"clean-engineering-model","format":"markdown","paths":["src/fulfilment/.context/fulfilment-model.drawio"]}`
3. `render.render {"guidance":"clean-engineering-model","format":"markdown","paths":["src/catalogue/catalogue.ts"]}`

## Expected
Each markdown names its own classes: Shipment and ExpressShipment in 2, Catalogue and Book in 3.

## Actual
1 is right (`## Cart`, `## CartLine`, `## Order`, `## Payment`). 2 answers `src\fulfilment\.context\fulfilment-model.md`, the person's model, which now reads:

    #

    ## Cart <<Aggregate Root>>

    + Cart(address: str, dispatched: bool, order: Order)
    ------
    + address: str
    + dispatched: bool
    + << association >> order: Order
    ----
    + Shipment(order: Order, address: str)
    + dispatch(): None
    + days_to_arrive(): int

    ## CartLine <<Entity>> : Shipment
    ...

3 writes `## Cart <<Aggregate Root>>` and `## CartLine <<Entity>>` over the bodies of Catalogue and Book. The classes take the first render's names by their place in the file (first class, second class); bodies, stereotypes and bases are the right model's, so `CartLine : Shipment` extends a class the file no longer holds. With the catalogue rendered first (`c3.json`), ordering came back as `# Catalogue`, `## Catalogue` (the Cart), `## Book` (the CartLine), `## Order`, `## Payment`, from python, typescript, drawio and whiteboard alike. A server restart gives the first render right names again. Renders to python, typescript, drawio and whiteboard in one server keep the right names. Results kept in `C:\dev\_et\round3\widget\drv\out\trips\alone` and `...\trips\*-to-markdown`.

Round 2's notes had "two model files rendered one after the other: each drawing holds its own classes"; that was to drawio. To markdown it fails.

## Tier that should catch it
Unit: `markdown_class_model_round_trip_spec.py` and `code_render_reuse_spec.py` render one model per adapter; an example that renders two different models with one `MarkdownCleanEngineeringModel` (or one `CleanEngineering`) and reads the second's class names would fail.
