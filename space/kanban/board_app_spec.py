"""The apps the session board's server serves, registered when the board is: the CDD Kanban and the Story UI editor."""
from expects import contain, equal, expect

from mamba import description, it

from harness.diagnostics.app import App
from space.kanban.board_app import APP_FOLDER, BOARD_APP_PORTS, KANBAN_APP, STORY_UI_APP, STORY_UI_FOLDER


with description("the session board's apps"):
    with it("should read the board's ports from the file its server reads"):
        expect(list(BOARD_APP_PORTS.of("board"))).to(equal(BOARD_APP_PORTS.file.read()["board"]))

    with it("should register the CDD Kanban and the Story UI editor with every app"):
        expect(App.registered()).to(contain(KANBAN_APP, STORY_UI_APP))

    with it("should give the CDD Kanban the board's app folder and ports"):
        expect((KANBAN_APP.folder, KANBAN_APP.ports)).to(equal((APP_FOLDER, BOARD_APP_PORTS.of("board"))))

    # The board's server serves the Story UI editor, whose code sits with the Stories practice it edits.
    with it("should open the Story UI editor on the board's port at /story-map, from the Stories practice's app folder"):
        expect((STORY_UI_APP.folder, STORY_UI_APP.ports, STORY_UI_APP.page)).to(equal((STORY_UI_FOLDER, BOARD_APP_PORTS.of("board"), "/story-map")))
