# harness/design_canvas

A *DesignCanvas* is the pages, boards, and artboard files of one Claude Design canvas; a practice lays out its own artboards with `artboard(...)`, `box(...)`, and `thumbnail(...)` and the shared look in `harness.design_canvas.look`, and hands them to the canvas, which decides where every file goes.

- **Purpose:** Let a practice publish its views as a Claude Design canvas without knowing the canvas's file layout, and regenerate it without overwriting what people edited.
- **Seam (terms):** DesignCanvas; `artboard(...)`, `box(...)`, `stem(...)`, `thumbnail(...)` (`canvas.py`); the look `LOOK`, `FONTS`, `BACKGROUND` (`look.py`)
- **Dependencies (one-way):** harness/installation

## DesignCanvas

The pages, boards and artboard files of one Claude Design canvas, and the files its project folder already holds, so a practice never reads the canvas project itself.

+ DesignCanvas(title: str, project: Path | None = None)
------
+ title: str
+ project: Path | None
+ launch_page: str | None
----
+ add_page(page_id: str, name: str): None
+ add_board(name: str, board: dict, text: str | None = None): None
+ artboards_in(folder: str): list[str]
+ holds(name: str): bool
+ size_of(name: str): int | None
+ stylesheets_linked_by(names: list[str]): list[str]
+ files(): dict[str, str]
+ write(root: str | Path): list[str]
