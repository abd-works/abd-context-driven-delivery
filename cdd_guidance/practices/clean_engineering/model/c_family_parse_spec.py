"""C-family parse: module-level functions stay off domain classes."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)


def _class(model, name: str):
    for module in model.modules:
        for oclass in module.classes:
            if oclass.name == name:
                return oclass
    return None


with description("CFamilyParse top-level functions"):
    with it("should keep module functions on _module, not the first class"):
        source = """
export class ValidationCode {
  constructor(public code: string) {}
}

export class AccountCredentials {
  register() {}
}

function accountRepositoryFor(credentials: AccountCredentials) {
  return credentials._repository;
}
"""
        model = TypeScriptCleanEngineeringModel().parse(source)
        validation = _class(model, "ValidationCode")
        module_holder = _class(model, "_module")
        expect([op.name for op in validation.operations]).to(equal(["constructor"]))
        expect([op.name for op in module_holder.operations]).to(equal(["accountRepositoryFor"]))

    with it("should keep a module function written as an exported arrow, with its return type"):
        source = """
export class TicketClient {
  select() {}
}

export const ticketOn = (page: BoardPage, name: string): TicketClient => {
  return page.ticket(name)
}

const slugsOf = (tile: Tile): string => tile.slugs.join(' ')
"""
        module_holder = _class(TypeScriptCleanEngineeringModel().parse(source), "_module")
        expect([(op.name, op.return_type) for op in module_holder.operations]).to(equal([("ticketOn", "TicketClient"), ("slugsOf", "string")]))


with description("CFamilyParse methods"):
    with it("should keep a method whose comment above it ends in a full stop"):
        source = """
export class BoardReader {
  constructor(private readonly page: BoardPage) {}

  // Reads can overlap, so an older answer never replaces a newer one.
  async refresh(): Promise<void> {
    await this.page.board.show()
  }
}
"""
        reader = _class(TypeScriptCleanEngineeringModel().parse(source), "BoardReader")
        expect([op.name for op in reader.operations]).to(equal(["constructor", "refresh"]))

    with it("should keep the method after one whose body holds a loop"):
        source = """
export class BoardReader {
  private async apply(shown: BoardData): Promise<void> {
    for (const announcement of shown.announcements) store.toast(announcement)
  }

  async refreshPressed(): Promise<void> {
    await this.refresh()
  }
}
"""
        reader = _class(TypeScriptCleanEngineeringModel().parse(source), "BoardReader")
        expect([op.name for op in reader.operations]).to(equal(["apply", "refreshPressed"]))


    with it("should read a method whose return type is an object of named fields, with that type and its own body"):
        source = """
export class BoardOnProject {
  page(): Promise<{ page: BoardPage; asked: Asked[] }> {
    return pageOf(this.board)
  }

  plain(): { a: number } {
    return makeA()
  }

  reset(): void {
    wipe(this.board)
  }
}
"""
        board = _class(TypeScriptCleanEngineeringModel().parse(source), "BoardOnProject")
        expect([(op.name, op.return_type, op.callees) for op in board.operations]).to(
            equal([("page", "Promise<{ page: BoardPage; asked: Asked[] }>", ["pageOf"]), ("plain", "{ a: number }", ["makeA"]), ("reset", "void", ["wipe"])])
        )

    with it("should read a method whose parameter has a function type, with that parameter and its own body"):
        source = """
export class RunningBoard {
  unreadPage(timed: (send: Send) => Send = send => send): { page: BoardPage } {
    return { page: new BoardPage(timed(sendOf(this))) }
  }

  close(): void {
    stop(this)
  }
}
"""
        board = _class(TypeScriptCleanEngineeringModel().parse(source), "RunningBoard")
        expect([(op.name, [parameter.name for parameter in op.parameters], op.return_type) for op in board.operations]).to(
            equal([("unreadPage", ["timed"], "{ page: BoardPage }"), ("close", [], "void")])
        )

with description("CFamilyParse fields"):
    with it("should hold a constructor parameter declared with an access modifier as a field, with its type"):
        source = """
export class OpenCardClient {
  constructor(private readonly page: BoardPage, public name: string, plain: number) {}

  closeCard(): void {
    this.page.store.change({ openCard: null })
  }
}
"""
        client = _class(TypeScriptCleanEngineeringModel().parse(source), "OpenCardClient")
        expect([(prop.name, prop.type_hint) for prop in client.properties]).to(equal([("page", "BoardPage"), ("name", "string")]))
