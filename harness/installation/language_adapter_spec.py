"""A language adapter: typed code for a CDD domain object, deployed by the installer like its other channels."""

import json
import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect, have_key, raise_error
from mamba import before, context, description, it

from harness.installation.install_diagnostics import InstallDiagnostics
from harness.installation.repository_toolsets import RepositoryToolsets

_REPO = Path(__file__).resolve().parents[2]
RepositoryToolsets(_REPO).ensure_import_path()

from harness.agent_tools.agent_tools import AgentToolSet  # noqa: E402
from harness.installation.data_class import (  # noqa: E402
    DataClass,
    Identity,
    ReferenceWithoutIdentityError,
    data_field,
    data_of,
    edits,
    identity,
    language_adapter,
)
from harness.installation.ide_layout import IdeLayout  # noqa: E402
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.installation.language_adapter import (  # noqa: E402
    LanguageAdapterInstallation,
    MissingIdentityError,
    PublishedSchema,
)

_KANBAN = (
    "space.kanban.board:Board",
    "space.kanban.ticket:Ticket",
    "space.kanban.ticket:FidelityProgress",
    "space.kanban.backlog_item:BacklogItem",
    "space.session.practice_session_output:PracticeSessionOutput",
)
_ADAPTERS = "language-adapters/typescript"
_IDENTITY_FLAG = Identity.flag


def _install(install_path, references=_KANBAN):
    adapters = LanguageAdapterInstallation(IdeLayout("Claude"), install_path, repo=_REPO)
    for reference in references:
        adapters.record(AgentToolSet.instantiate(reference))
    adapters.write_all()
    return adapters


def _between(text, start, end):
    return text[text.index(start) : text.index(end)]


with description("a language adapter"):
    with description("a toolset annotated for a language"):
        with it("should name that language"):
            @language_adapter(language="typescript")
            class Annotated:
                pass

            expect(DataClass(Annotated).languages).to(equal(("typescript",)))

        with it("should name the field of its data that holds an object's name"):
            @identity("name")
            class Named:
                pass

            expect(DataClass(Named).identity).to(equal(("name",)))

        with it("should name a subclass as its base is named"):
            @identity("name")
            class Named:
                pass

            class Kind(Named):
                pass

            expect(DataClass(Kind).identity).to(equal(("name",)))

        with it("should name the fields an operation changes when its arguments are named differently"):
            @edits("title")
            def rename(new_title):
                return new_title

            expect(DataClass(type(None)).edited_by(rename)).to(equal(("title",)))

        with context("that no annotation names"):
            with it("should name no language"):
                class Unmarked:
                    pass

                expect(DataClass(Unmarked).languages).to(equal(()))

    with description("the data of a domain object"):
        with before.all:
            class Place:
                def __init__(self, folder):
                    self._folder = folder

                @property
                @data_field
                def folder(self) -> Path:
                    return self._folder

            @identity("name")
            class Stage:
                def __init__(self, name, cards):
                    self._name = name
                    self._cards = cards

                @property
                @data_field
                def name(self) -> str:
                    return self._name

                @property
                @data_field
                def cards(self) -> list:
                    return self._cards

            class Card:
                def __init__(self, title, places):
                    self._title = title
                    self._places = places
                    self._stage = Stage("Discovery", [self])

                @property
                @data_field
                def title(self) -> str:
                    return self._title

                @property
                @data_field(key="column", reference=True)
                def stage(self) -> Stage:
                    return self._stage

                @property
                @data_field
                def places(self) -> list[Place]:
                    return self._places

                @property
                def unshown(self) -> str:
                    return "kept in Python"

            class PinnedCard(Card):
                @property
                @data_field
                def is_pinned(self) -> bool:
                    return True

                @property
                def title(self) -> str:
                    return f"Pinned: {self._title}"

            self.card_class, self.pinned_class = Card, PinnedCard
            self.card = PinnedCard("Visits", [Place(Path("notes"))])

        with it("should be the properties annotated as its data, under their names"):
            expect(list(DataClass(self.card_class).fields)).to(equal(["title", "column", "places"]))

        with it("should keep the data a base class annotates, ahead of its own"):
            expect(list(DataClass(self.pinned_class).fields)).to(equal(["title", "column", "places", "is_pinned"]))

        with it("should be written as a plain value, each object it holds written as its own data"):
            expect(data_of(self.card)).to(equal({"title": "Pinned: Visits", "column": {"name": "Discovery"}, "places": [{"folder": "notes"}], "is_pinned": True}))

        with it("should send an object a reference field holds by that object's identity alone, so an object can name the one holding it"):
            expect(data_of(self.card)["column"]).to(equal({"name": "Discovery"}))

        with context("whose reference field holds an object with no identity"):
            with it("should refuse, because nothing could say which object it names"):
                class Unnamed:
                    pass

                class Holder:
                    @property
                    @data_field(reference=True)
                    def held(self) -> Unnamed:
                        return Unnamed()

                expect(lambda: data_of(Holder())).to(raise_error(ReferenceWithoutIdentityError))

        with it("should read a field a subclass overrides from the subclass, though only the base annotates it"):
            expect(data_of(self.card)["title"]).to(equal("Pinned: Visits"))

        with it("should leave out a property it does not annotate"):
            expect(data_of(self.card)).not_to(have_key("unshown"))

    with description("the installation of an annotated toolset"):
        with before.all:
            self.install_path = Path(tempfile.mkdtemp(prefix="language-adapter-"))
            self.adapters = _install(self.install_path)
            self.root = self.install_path / _ADAPTERS
            self.ticket = (self.root / "space/kanban/ticket.ts").read_text(encoding="utf-8")
            self.board = (self.root / "space/kanban/board.ts").read_text(encoding="utf-8")
            self.backlog_item = (self.root / "space/kanban/backlog-item.ts").read_text(encoding="utf-8")
            self.progress = (self.root / "space/kanban/fidelity-progress.ts").read_text(encoding="utf-8")
            self.practice = (self.root / "space/session/practice-session-output.ts").read_text(encoding="utf-8")

        with it("should mirror the folders the toolset's source sits in, with every generated class of an object in one file"):
            written = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*.ts*"))
            expect(written).to(equal([
                "cdd-connection.ts",
                "cdd-shared.ts",
                "cdd-views.tsx",
                "space/kanban/backlog-item-views.tsx",
                "space/kanban/backlog-item.ts",
                "space/kanban/board-views.tsx",
                "space/kanban/board.ts",
                "space/kanban/fidelity-progress-views.tsx",
                "space/kanban/fidelity-progress.ts",
                "space/kanban/ticket-views.tsx",
                "space/kanban/ticket.ts",
                "space/session/practice-session-output-views.tsx",
                "space/session/practice-session-output.ts",
            ]))

        with it("should declare ES modules, so Node loads the files wherever the install sits"):
            manifest = json.loads((self.root / "package.json").read_text(encoding="utf-8"))
            expect(manifest).to(equal({"private": True, "type": "module"}))

        with it("should say it is generated"):
            expect(self.ticket.splitlines()[0]).to(contain("Generated by cdd"))

        with it("should track every file it writes, so clean removes them"):
            tracked = []
            adapters = LanguageAdapterInstallation(IdeLayout("Claude"), self.install_path, repo=_REPO)
            adapters.track_writes_with(tracked.append)
            adapters.record(AgentToolSet.instantiate("space.kanban.ticket:Ticket"))
            adapters.write_all()
            expect(sorted(path.name for path in tracked)).to(equal(["cdd-connection.ts", "cdd-shared.ts", "cdd-views.tsx", "package.json", "ticket-views.tsx", "ticket.ts"]))

        with context("whose tools run on the one toolset a project holds, which no call loads by name"):
            with before.all:
                install_path = Path(tempfile.mkdtemp(prefix="language-adapter-"))
                _install(install_path, ("harness.graph.graph:Graph",))
                self.graph = (install_path / _ADAPTERS / "harness/graph/graph.ts").read_text(encoding="utf-8")

            with it("should type data that holds a type another of its modules defines, as the graph's filtered nodes type their rules"):
                expect(self.graph).to(contain("rules: GraphRuleData[]"))

            with it("should call each operation on the client the page holds, not on the class"):
                expect(self.graph).to(contain("  inventory(): Promise<InventoryData | null> {"))

        with context("that has no annotation"):
            with it("should write nothing"):
                install_path = Path(tempfile.mkdtemp(prefix="language-adapter-"))
                _install(install_path, ("tools.echo.echo:Echo",))
                expect((install_path / _ADAPTERS).exists()).to(be_false)

        with context("whose tools load one object by name, with no identity on its annotation"):
            with it("should refuse, because a browser object could not say which object its routes act on"):
                ticket_class = type(AgentToolSet.instantiate("space.kanban.ticket:Ticket"))
                named = getattr(ticket_class, _IDENTITY_FLAG)
                delattr(ticket_class, _IDENTITY_FLAG)
                try:
                    expect(lambda: _install(Path(tempfile.mkdtemp(prefix="language-adapter-")))).to(raise_error(MissingIdentityError))
                finally:
                    setattr(ticket_class, _IDENTITY_FLAG, named)

        with description("its connection"):
            with before.all:
                self.connection = (self.root / "cdd-connection.ts").read_text(encoding="utf-8")

            with it("should be one class that carries every call"):
                expect(self.connection).to(contain("export class CddConnection {"))

            with it("should import only Node's own modules, so the install needs no package"):
                imports = [line for line in self.connection.splitlines() if line.startswith("import ") and "from './" not in line]
                expect(all("from 'node:" in line for line in imports)).to(be_true)

            with it("should start cdd from the checkout it was installed from"):
                expect(self.connection).to(contain(f"const SOURCE_ROOT = {json.dumps(str(_REPO))}"))

            with it("should raise the text of an answer that is not JSON"):
                expect(self.connection).to(contain("throw new CddToolError(tool, text)"))

            with it("should give up on a call after ten minutes"):
                expect(self.connection).to(contain("const LONGEST_TOOL_MILLISECONDS = 600_000"))

            with it("should ask for the progress of every tool call under that call's own id"):
                expect(self.connection).to(contain("_meta: { progressToken: id }"))

            with it("should keep the newest step each running call reported"):
                expect(self.connection).to(contain("progress(): CddProgress[] {"))

        with description("its shared code"):
            with it("should import only types, so a browser loads nothing of Node"):
                shared = (self.root / "cdd-shared.ts").read_text(encoding="utf-8")
                imports = [line for line in shared.splitlines() if line.startswith("import ")]
                expect(all(line.startswith("import type ") for line in imports)).to(be_true)

            with it("should answer the steps of the running calls at one shared route"):
                shared = (self.root / "cdd-shared.ts").read_text(encoding="utf-8")
                expect(shared).to(contain("{ path: '/cdd/progress', run: async cdd => cdd.progress() }"))

        with description("its data"):
            with it("should state the data the Python class annotates"):
                expect(self.ticket).to(contain("export type TicketData = {"))
                expect(self.ticket).to(contain("  is_done: boolean\n"))

            with it("should keep a field that may be absent optional"):
                expect(self.board).to(contain("  wip_limit?: number\n"))

            with it("should keep a field that may be null nullable"):
                expect(self.ticket).to(contain("  next: { ticket: { name: string }; fidelity: { slug: string } } | null\n"))

            with it("should name a referenced object by its identity, and an identity field that is an object by that object's own identity"):
                expect(self.progress).to(contain("  ticket: { name: string }\n"))

            with it("should read an identity field that is an object by the field that names it"):
                expect(self.progress).to(contain("ticket: string = state?.ticket?.name ?? '', fidelity: string = state?.fidelity?.slug ?? ''"))

            with it("should state a nested shape in the file that uses it"):
                expect(self.ticket).to(contain("export type ReportData = {"))

            with it("should type a field holding objects as their data, named after their class"):
                expect(self.ticket).to(contain("  source: SourceLineData[]\n"))

            with it("should type a field holding another annotated object as that object's data, imported from its file"):
                expect(self.board).to(contain("  in_progress?: TicketData[]\n"))

            with context("with a field that takes one of a few named words"):
                with it("should allow only those words"):
                    install_path = Path(tempfile.mkdtemp(prefix="language-adapter-"))
                    _install(install_path, ("harness.chat.chat:Chat",))
                    chat = (install_path / _ADAPTERS / "harness/chat/chat.ts").read_text(encoding="utf-8")
                    expect(chat).to(contain("  state: 'waiting' | 'taken' | 'shown' | 'done' | 'failed'\n"))

        with description("its shared base"):
            with before.all:
                self.base = _between(self.ticket, "export class Ticket {", "export class TicketClientGenerated")

            with it("should read each field in camelCase"):
                expect(self.base).to(contain("get isDone(): boolean {\n    return this.#read().is_done\n  }"))

            with it("should serialize back to exactly what Python sent"):
                expect(self.base).to(contain("toJSON(): TicketData {\n    return this.#read()\n  }"))

            with it("should let its subtypes take on new state"):
                expect(self.base).to(contain("protected changed(state: TicketData): this {"))

            with it("should tell whatever is drawing it when it takes on new state"):
                expect(self.base).to(contain("for (const listener of this.#listeners) listener()"))

            with it("should make no call, so nothing reaches a tool through the base itself"):
                expect("call<" in self.base or "post<" in self.base).to(be_false)

        with description("its server adapter"):
            with it("should extend the shared base"):
                expect(self.ticket).to(contain("export class TicketAdapter extends Ticket {"))

            with it("should call only its own object's tools, so no connector knows every tool"):
                expect("board.show" in self.ticket).to(be_false)

            with context("for an object loaded by its identity"):
                with it("should hold the identity, so a caller never passes it again"):
                    expect(self.ticket).to(contain("constructor(protected readonly cdd: CddConnection, ticket: string, state: TicketData | null = null) {"))

                with it("should send the identity under its Python name"):
                    expect(self.ticket).to(contain("'ticket.move_next', { ticket: this.#ticket }"))

                with it("should build the adapter for the object a request names"):
                    expect(self.ticket).to(contain("static fromRequest(cdd: CddConnection, request: CddRequest): TicketAdapter {"))

            with context("for an object with no identity"):
                with it("should need only the connection"):
                    expect(self.board).to(contain("constructor(protected readonly cdd: CddConnection, state: BoardData | null = null) {"))

            with context("for an operation with its own arguments"):
                with it("should type each argument from the published schema"):
                    expect(self.practice).to(contain("async enable(isEnabled: boolean): Promise<this> {"))

                with it("should mark an argument with a Python default as optional"):
                    expect(self.ticket).to(contain("async close(leaving?: string[] | null): Promise<this> {"))

                with it("should send camelCase arguments under their Python names"):
                    expect(self.practice).to(contain("is_enabled: isEnabled"))

            with context("for a result"):
                with it("should take on the object's own state its tool returns"):
                    expect(self.ticket).to(contain("return this.changed(await this.cdd.call<TicketData>('ticket.move_next'"))

                with it("should import another object it returns"):
                    expect(self.ticket).to(contain("import type { BacklogItemData } from './backlog-item'"))

                with it("should leave a choice of objects as their data"):
                    expect(self.ticket).to(contain("movePrevious(): Promise<TicketData | BacklogItemData>"))

                with it("should type a shape Python declares"):
                    expect(self.progress).to(contain("report(): Promise<ReportData>"))

                with it("should type a list of strings"):
                    expect(self.board).to(contain("Promise<string[]>"))

            with context("for a class operation, which no loaded object runs"):
                with it("should be a static operation that takes the connection and returns the new object's data"):
                    expect(self.ticket).to(contain("static create(cdd: CddConnection, title: string, scope?: string, parent?: string, path?: string): Promise<TicketData>"))

        with description("its browser client"):
            with it("should extend the shared base"):
                expect(self.ticket).to(contain("export class TicketClientGenerated extends Ticket {"))

            with it("should take its identity from the field the annotation names"):
                expect(self.ticket).to(contain("ticket: string = state?.name ?? ''"))

            with it("should type a reference field as the identity of the object it names"):
                expect(self.ticket).to(contain("  column: { name: string }"))

            with it("should type a reference field that names several objects as a list of their identities"):
                expect(self.board).to(contain("  open_tickets: { name: string }[]\n"))

            with it("should show a reference field in its view by the field that names the object it refers to"):
                views = (self.root / "space/kanban/ticket-views.tsx").read_text(encoding="utf-8")
                expect(views).to(contain('<ReadOnlyField label="Column" value={ticket.column.name} />'))

            with it("should post to its object's route, with the name safe in the path"):
                expect(self.ticket).to(contain("this.api.post<TicketData>(`/ticket/${encodeURIComponent(this.#ticket)}/move-next`, {})"))

            with it("should send arguments under their Python names"):
                expect(self.practice).to(contain("{ is_enabled: isEnabled }"))

            with it("should keep its state when the page has already shown a failure"):
                expect(self.ticket).to(contain("return state ? this.changed(state) : null"))

            with context("for page code that knows only an object's name"):
                with it("should act on that object before it has read it"):
                    expect(self.ticket).to(contain("static named(api: CddApi, ticket: string): TicketClientGenerated {"))

            with context("for a class operation"):
                with it("should post with the API it is given and return the new object's data"):
                    expect(self.backlog_item).to(contain("static create(api: CddApi, title: string, text?: string): Promise<BacklogItemData | null> {"))

        with description("its routes"):
            with it("should give each tool one path under its object and identity"):
                expect(self.ticket).to(contain("path: '/ticket/:ticket/move-next'"))

            with it("should run the tool through the server adapter for the object the path names"):
                expect(self.ticket).to(contain("TicketAdapter.fromRequest(cdd, request).moveNext()"))

            with it("should read the operation's arguments from the request, checked against the published schema"):
                expect(self.practice).to(contain('readArguments<{ is_enabled: boolean }>(request, {"is_enabled": {"type": "boolean"}}, ["is_enabled"])'))

            with context("for an object no tool loads by name"):
                with it("should leave the name out of the path"):
                    expect(self.board).to(contain("path: '/board/show', run: (cdd, request) => new BoardAdapter(cdd).show()"))

    with description("the generated views of an annotated toolset"):
        with before.all:
            install_path = Path(tempfile.mkdtemp(prefix="language-adapter-views-"))
            _install(install_path, ("harness.installation._examples.note:Note", "space.session.file_manager:FileManager"))
            root = install_path / _ADAPTERS
            self.note = (root / "harness/installation/_examples/note.ts").read_text(encoding="utf-8")
            self.views = (root / "harness/installation/_examples/note-views.tsx").read_text(encoding="utf-8")
            self.shared_views = (root / "cdd-views.tsx").read_text(encoding="utf-8")
            self.file_views = (root / "cdd-files.tsx").read_text(encoding="utf-8")

        with it("should take React from the application, the only package it imports"):
            imports = [line for line in self.shared_views.splitlines() if line.startswith("import ") and " from '" in line and "from './" not in line]
            expect(all(line.endswith("from 'react'") for line in imports)).to(be_true)

        with it("should say which JSX it uses, since the install has no settings of its own"):
            expect(self.views).to(contain("/** @jsxRuntime automatic @jsxImportSource react */"))

        with it("should draw the object again whenever its client takes on new state"):
            expect(self.views).to(contain("export function useNote<Client extends Note>(client: Client): Client {"))

        with context("for a field an operation's argument of the same name changes"):
            with it("should make it an input that saves through that operation"):
                expect(self.views).to(contain('<EditableField label="Text" kind="text" value={note.text} onSave={value => note.updateText(value as string)} />'))

        with context("for a field an operation annotates with @edits"):
            with it("should make it an input that saves through that operation"):
                expect(self.views).to(contain("onSave={value => note.rename(value as string)}"))

        with context("for a field no operation changes"):
            with it("should show it read-only"):
                expect(self.views).to(contain('<ReadOnlyField label="Is pinned" value={note.isPinned} />'))

        with context("for an operation with no arguments of its own"):
            with it("should draw a button"):
                expect(self.views).to(contain('<OperationForm label="Pin" inputs={[]} onRun={() => note.pin()} />'))

        with context("for an operation that answers with something other than the object"):
            with it("should show its answer"):
                expect(self.views).to(contain("showsResult onRun={() => note.wordCount()}"))

        with context("for an operation that edits a field"):
            with it("should not draw it again as a form"):
                expect(self.views).to(contain("operations?: Partial<Record<'pin' | 'wordCount',"))

        with context("for a field the page draws itself"):
            with it("should draw the page's own field in its place"):
                expect(self.views).to(contain("{fields.title ? fields.title(note) :"))

        with context("for a class operation that answers with a new object"):
            with it("should draw a form that creates it"):
                expect(self.views).to(contain("export function NoteNewViewGenerated({ api, onCreated }: NoteNewViewProps): ReactNode {"))

        with context("for a field Python annotates as a source file"):
            with it("should type it as the path it holds"):
                expect(self.note).to(contain("  source: string\n"))

            with it("should open it in the shared source view at the line the same data holds"):
                expect(self.views).to(contain('<SourceField api={note.api} label="Source" path={note.source} line={note.line} />'))

        with it("should show the newest step of each running call while a page waits"):
            expect(self.shared_views).to(contain("export function ProgressViewGenerated("))

        with description("the shared file views"):
            with it("should read files through the file manager's generated client"):
                expect(self.file_views).to(contain("from './space/session/file-manager'"))

            with it("should take Monaco from the application"):
                expect(self.file_views).to(contain("from '@monaco-editor/react'"))

    with description("the installation of a toolset whose objects are named, with an operation that names none"):
        with before.all:
            out = Path(tempfile.mkdtemp(prefix="language-adapter-session-"))
            _install(out, ["space.session.session:Session"])
            self.session = (out / _ADAPTERS / "space/session/session.ts").read_text(encoding="utf-8")

        with it("should route the operation to the class, since it acts on no one object"):
            expect(self.session).to(contain("run: (cdd, request) => SessionAdapter.recordDecisionsSession(cdd) }"))

    with description("a published schema"):
        with it("should keep only what checking a sent value needs"):
            expect(PublishedSchema({"type": "string", "title": "Stage", "default": ""}).argument_check).to(equal({"type": "string"}))

        with it("should become a TypeScript array"):
            expect(PublishedSchema({"type": "array", "items": {"type": "string"}}).typescript_type).to(equal("string[]"))

        with context("with a union"):
            with it("should keep every option"):
                expect(PublishedSchema({"anyOf": [{"type": "integer"}, {"type": "null"}]}).typescript_type).to(equal("number | null"))

    with description("the installer"):
        with it("should deploy this channel beside the others"):
            expect("language-adapter" in InstallDiagnostics.CHANNELS).to(be_true)


with description("the TypeScript files of the kanban toolsets being written"):
    with it("should make each class's data shape once for each file it is written into"):
        import harness.installation.language_adapter as language_adapter

        made: list[tuple[int, type]] = []
        original = language_adapter._DataShape

        class CountedShape(original):
            def __init__(self, shape, owner) -> None:
                made.append((id(owner), shape))
                super().__init__(shape, owner)

        language_adapter._DataShape = CountedShape
        try:
            _install(Path(tempfile.mkdtemp(prefix="adapter-shapes-")))
        finally:
            language_adapter._DataShape = original
        expect(len(made)).to(equal(len(set(made))))
